import requests

def getBookInfo(isbn:str):
      req = requests.get('https://www.googleapis.com/books/v1/volumes?q=isbn:'+isbn)
      if req.status_code == requests.status_codes.ok:
        return req.json()