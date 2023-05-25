from ebooklib import epub
from ebooklib import utils
import xml.etree.ElementTree as ET
from models import Book
from app import db
from sqlalchemy import and_
import os
import json
import itertools
from multiprocessing.pool import ThreadPool
import time
from threading import Thread, Lock
import gpt_api

OPF = '{http://www.idpf.org/2007/opf}'
XHTML = '{http://www.w3.org/1999/xhtml}'
TAG_P = XHTML + 'p'
ATTR_CFI = 'cfi'

ASK_COUNT = 64

_lock:Lock = Lock()
_threads = {}

def processing(id:int)->bool:
    return id in _threads
def join(id:int):
    if id in _threads:
        print('waiting...')
        _threads[id].join()

def handle_post(path:str):
    reader = epub.EpubReader(path, {'ignore_ncx':True})
    reader.load()
    reader.process()

    title = str(reader.book.get_metadata('DC', 'title'))
    language = str(reader.book.get_metadata('DC', 'language'))
    identifier = str(reader.book.get_metadata('DC', 'identifier'))

    record : Book = Book.query.filter(and_(Book.title==title, Book.identifier==identifier, Book.language==language)).first()
    
    if record is None:
        record = Book(title=title, language=language, identifier=identifier, path=path, result=None)
        db.session.add(record)
        db.session.commit()
        t = Thread(target=_analyze, args=(record.id, reader))
        _lock.acquire()
        _threads[int(record.id)] = t
        _lock.release()
        t.start()
    elif not record.result_exists() and not processing(int(record.id)):
        record.remove_book()
        record.path = path
        db.session.commit()
        t = Thread(target=_analyze, args=(record.id, reader))
        _lock.acquire()
        _threads[int(record.id)] = t
        _lock.release()
        t.start()
    else:
        os.remove(path)
    return str(record.id)

def _analyze(id:int, reader:epub.EpubReader):
    
    def _askgpt(node : ET.Element):
        if node.text is None:
            return None        
        emotion = {}
        for i in gpt_api.getLogProbEmotionFromGPT(node.text):
            for j in i.items():
                emotion[j[0].strip()] = pow(10, j[1])     
        return {
            "cfi" : node.get(ATTR_CFI),
            "content": node.text,
            "emotion": emotion,
            #"color" : "#000000",
            #"weather" : "rain"
            }
    
    book:Book = Book.query.get(id)  
    result:str
    path = os.path.join('raw', ''.join((str(book.id), '.json')))

    if book.raw_result_exists():
        with open(path, 'r', encoding='utf-8') as f:
            result = f.read()
    else:
        start_time = time.time()
        title = str(reader.book.get_metadata('DC', 'title'))
        print('ASKING GPT.....', title)
        documents = parse(reader)
        pool = ThreadPool(ASK_COUNT)
        answer = pool.map(_askgpt, itertools.chain.from_iterable([doc[1].iter(TAG_P) for doc in documents]))
        answer = [i for i in answer if i is not None]
        pool.close()
        pool.join()
        print('GPT ANSWERED...', title,
              '\nCOUNT..........', len(answer),
              '\nSECONDS........', (time.time() - start_time)
              )

        book.raw = path
        result = json.dumps({'data':answer}, ensure_ascii=False)
        os.makedirs('raw', exist_ok=True)
        with open(path, 'w+', encoding='utf-8') as f:
            f.write(result)

    os.makedirs('result', exist_ok=True)
    path = os.path.join('result', ''.join((str(book.id), '.json')))
    with open(path, 'w+', encoding='utf-8') as f:
        f.write(json.dumps({'data':answer}, ensure_ascii=False))    
    book.result = path
    db.session.commit()

    _lock.acquire()
    del(_threads[int(book.id)])
    _lock.release()
    return

def parse(reader:epub.EpubReader):
    def _handle_node(node : ET.Element, cfi:str):
        if not node.get('id') is None:
            cfi = '{}[{}]'.format(cfi, node.get('id'))
        if node.tag == TAG_P:            
            node.set(ATTR_CFI, cfi)
            return
        if len(node) == 0:
            return
        i = 0
        for n in node:
            i += 2
            _handle_node(n, '{}/{}'.format(cfi, i))

    book = reader.book
    spine = reader.container.find(OPF + 'spine')
    documents = []
    i = 0
    doc : ET.Element
    for doc in spine:
        idref = doc.get('idref')
        id = doc.get('id')
        i += 2
        cfi = '/6/{}!'.format(i) if id is None else '/6/{}}[{}]!'.format(i, id)

        item:epub.EpubItem = book.get_item_with_id(idref)
        tree:ET.ElementTree = utils.parse_string(item.get_content())
        node:ET.Element = tree.getroot()

        _handle_node(node, cfi)
        documents.append((item.file_name, tree))
    return documents