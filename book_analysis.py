from ebooklib import epub
from ebooklib import utils
import xml.etree.ElementTree as ET
from lxml import etree
from models import Book
from app import db
from sqlalchemy import and_
import os
import json
import itertools
from multiprocessing.pool import ThreadPool
import time
import random

OPF = '{http://www.idpf.org/2007/opf}'
XHTML = '{http://www.w3.org/1999/xhtml}'
TAG_P = XHTML + 'p'
ATTR_CFI = 'cfi'

ASK_COUNT = 64

class Generator:
    container : ET.ElementTree
    documents = []

    def debug_print_container(self):
        print(etree.tostring(self.container, pretty_print=True, encoding='unicode'))

    def debug_print_whole(self):
        for doc in self.documents:
            print('===========================')
            print('file_name:', doc[0])
            print('---------------------------')
            print(etree.tostring(doc[1], pretty_print=True, encoding='unicode'))

    def debug_print_paragraph(self):
        for doc in self.documents:
            print('===========================')
            print('file_name:', doc[0])
            print('---------------------------')
            node : ET.Element
            for node in doc[1].iter(TAG_P):
                print(etree.tostring(node, pretty_print=True, encoding='unicode'))

    def _handle_node(self, node : ET.Element, cfi:str):
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
            self._handle_node(n, '{}/{}'.format(cfi, i))



    def __init__(self, reader:epub.EpubReader):
        book = reader.book

        i = 0
        item : epub.EpubItem
        doc : ET.Element
        node : ET.Element
        tree : ET.ElementTree
        spine = reader.container.find(OPF + 'spine')

        for doc in spine:
            idref = doc.get('idref')
            id = doc.get('id')
            i += 2
            cfi = '/6/{}!'.format(i) if id is None else '/6/{}}[{}]!'.format(i, id)

            item = book.get_item_with_id(idref)
            tree = utils.parse_string(item.get_content())
            node = tree.getroot()

            self._handle_node(node, cfi)
            self.documents.append((item.file_name, tree))


# g = Generator('alice.epub')

# start_time = time.time()
# for i in g.analyze():
#     print(i)
# print(time.time() - start_time, "seconds")

def search_book(path:str):
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
        analyze(record, reader)
    else:
        # no result
        if not record.result_exists():
            if not record.processing:
                record.path = path
                analyze(record, reader)

    os.remove(path)
    return str(record.id)

def analyze(book:Book, reader:epub.EpubReader):

    def _askgpt(node : ET.Element):
        print(node.get(ATTR_CFI))
        if node.text is None:
            return None
        time.sleep(random.uniform(0.5, 2))
        return {
            "cfi" : node.get(ATTR_CFI),
            "emotion":{"joy":0.2, "excitement":0.5, "gratitude":0.7 },
            "color" : "#0066AA",
            "weather" : "rain"
            }
    
    book.processing = True
    db.session.commit()

    gen = Generator(reader)
    pool = ThreadPool(ASK_COUNT)
    result = pool.map(_askgpt, itertools.chain.from_iterable([doc[1].iter(TAG_P) for doc in gen.documents]))
    result = [i for i in result if i is not None]

    os.makedirs('result', exist_ok=True)
    path = os.path.join('result', ''.join((str(book.id), '.json')))
    with open(path, 'w+', encoding='utf-8') as res:
        res.write(json.dumps({'data':result}, ensure_ascii=False))
    pool.close()
    pool.join()
    
    book.result = path
    book.processing = False
    db.session.commit()
    return