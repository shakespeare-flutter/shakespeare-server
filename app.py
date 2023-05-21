from flask import Flask
from database import My_SQLAlchemy
from dotenv import load_dotenv
### from gpt_api import getEmotionFromGPT # test

import config
db = My_SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # load env
    load_dotenv()

    # ORM
    db.init_app(app)
    import models

    # blueprint
    import views.views as views
    app.register_blueprint(views.bp)
    
    return app