from models import Book
from app import db

def analyze(id:Book, content:str):
    id.content = content
    db.session.commit()
    return