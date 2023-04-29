import enum
from app import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text(), nullable=True)

class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(256), nullable=False)