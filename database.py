import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import flask
from greenlet import getcurrent

class My_SQLAlchemy:
    def __init__(self):
        self.Base = declarative_base()

    def init_app(self, app):
        self.engine = sqlalchemy.create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        self.sessionmaker = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
            )
        self.session = scoped_session(
            self.sessionmaker,
            scopefunc=getcurrent
            )        
        self.Base.query = self.session.query_property()
        self.Base.metadata.create_all(bind=self.engine)