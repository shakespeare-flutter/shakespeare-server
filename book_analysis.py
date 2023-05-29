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
from math import exp
import numpy as np
import music_recommend

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
    db.session.close()
    return str(record.id)

def _analyze(id:int, reader:epub.EpubReader):
    
    def _askgpt(node : ET.Element):
        if node.text is None:
            return None 
        emotion = {}
        for i in gpt_api.getLogProbEmotionFromGPT(node.text):
            for j in i.items():
                emotion[j[0].strip()] = exp(j[1])     
        return {
            "cfi" : node.get(ATTR_CFI),
            "content": node.text,
            "emotion": emotion,
            "color" : "#000000",
            "weather" : "rain"
            }
    
    book:Book = Book.query.get(id)
    path = os.path.join('raw', ''.join((str(book.id), '.json')))

    if not book.raw_result_exists():
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

    raw_values, _, cfi = get_raw_values(path)
    rounded_values, _ = get_rounded_values(raw_values)
    values = clamp_values(rounded_values)
    music = [music_recommend.get_music(v, None, None) for v in values]

    result = data_to_json(cfi, values, None, None, music)

    os.makedirs('result', exist_ok=True)
    path = os.path.join('result', ''.join((str(book.id), '.json')))
    with open(path, 'w+', encoding='utf-8') as f:
        f.write(json.dumps({'data':result}, ensure_ascii=False))    
    book.result = path
    db.session.commit()

    _lock.acquire()
    del(_threads[int(book.id)])
    _lock.release()
    db.session.close()
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


EMOTION = ['admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring', 'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval', 'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief', 'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization', 'relief', 'remorse', 'sadness', 'surprise', 'neutral']

# WINDOW SHAPE FUNCTIONS
def normal_dist(x, deviation):
    y = np.exp(-0.5*(x/deviation)**2)
    return y / sum(y)
def rectangle(x):
    return np.ones(shape=np.shape(x)) / len(x)
def pyramid(x):
    y = np.abs(x)
    y = 1 - y / np.max(y)
    return y / np.sum(y)

def get_raw_values(file_name:str):
    with open(file_name, "r", encoding='utf-8') as f:
        jsn = json.load(f)
    data = [i['emotion'] for i in jsn['data']]
    cfi = [i['cfi'] for i in jsn['data']]
    result = {}
    for E in EMOTION:
        result[E] = [e[E] if E in e else 0 for e in data]
    max_values = [max(e,key=e.get) for e in data]
    return result, max_values, cfi

HALF_SIZE = 2
def get_rounded_values(values:dict):
    shift = np.arange(-HALF_SIZE, HALF_SIZE+1)
    window = normal_dist(shift, 1)
    length = len(values[EMOTION[0]])
    
    rounded = {}
    for E in EMOTION:
        origin = values[E]
        temp = np.zeros(length)
        for x, y in zip(shift, window):
            v1 =  np.roll(origin, x)
            if x < 0:
                v1[x:] = v1[x]
            elif x > 0:
                v1[:x] = v1[x]
            temp += v1 * y
        rounded[E] = temp
    max_values = [max([E for E in EMOTION],key=lambda E : rounded[E][i]) for i in range(length)]
    return rounded, max_values

CRITERIA = 0.05
def clamp_values(values:dict):
    length = len(values[EMOTION[0]])
    result = [None] * length
    for i in range(length):
        e = {}
        for E in EMOTION:
            v = values[E][i]
            if v > CRITERIA:
                e[E] = v
        result[i] = e
    return result

def data_to_json(cfi, emotions, weather, color, music):
    length = len(emotions)
    result = [None] * length
    for i in range(length):
        result[i] = {
            "cfi" : cfi[i],
            "emotion": emotions[i],
            "color" : "#000000",
            "weather" : "rain",
            "music" : str(music[i])
            }
    return result