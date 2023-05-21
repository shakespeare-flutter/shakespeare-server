from app import db
import os.path
from sqlalchemy import Column, Integer, String

class Book(db.Base):
    __tablename__ = 'Book'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    identifier = Column(String, nullable=False)
    language = Column(String, nullable=False)

    path = Column(String, nullable=True)
    result = Column(String, nullable=True)

    def result_exists(self):
        return False if self.result is None else os.path.isfile(self.result)
    def remove_book(self):
        if False if self.path is None else os.path.isfile(self.path):
            os.remove(self.path)