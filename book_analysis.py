from models import Book
from app import db
import time

def analyze(book:Book):
    book.processing = True
    db.session.commit()
    for i in range(10):
        print('processing...' + book.identifier)
        time.sleep(1)
    book.result = example
    book.processing = False
    db.session.commit()
    return

example = """{
    data:[
        {
            "start" : "0",
            "end" : "10",
            "emotion":{
                "happy":"4",
                "joy":"7"
                },
            "color" : "red",
            "weather" : "rain"
        },
        {
            "start" : "10",
            "end" : "20",
            "emotion" : {
                "happy":"1",
                "joy":"4"
                },
            "color" : "white",
            "weather" : "cloudy"
        }
    ]
}"""