from app import db
import os.path

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    identifier = db.Column(db.String(), nullable=False)
    language = db.Column(db.String(), nullable=False)

    processing = db.Column(db.Boolean, default=False, nullable=False)

    path = db.Column(db.String(), nullable=True)
    result = db.Column(db.String(), nullable=True)

    def result_exists(self):
        return False if self.result is None else os.path.isfile(self.result)    
    def book_file_exists(self):
        return False if self.path is None else os.path.isfile(self.path)