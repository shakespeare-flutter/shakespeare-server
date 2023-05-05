import requests

identifier = 'test_alice'
epub_path = 'books/alice.txt'
server_address = 'http://localhost:5000/'
timeout = 10


def post_epub():
    with open(epub_path, 'r', encoding='UTF8') as f:        
        content = '\n'.join(f.readlines())    
        try:
            res = requests.post('{address}book?id={id}'.format(address=server_address, id=identifier), headers={'Content-Type': 'application/json'}, json={'content': content}, timeout=timeout)
        except TimeoutError as e:
            return e
        return res

print(post_epub())