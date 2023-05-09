from app import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(64), nullable=False)
    processing = db.Column(db.Boolean, default=False, nullable=False)
    content = db.Column(db.Text(), nullable=True)
    result = db.Column(db.Text(), nullable=True)