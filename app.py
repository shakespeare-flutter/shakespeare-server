from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
### from gpt_api import getEmotionFromGPT # test

import config
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # load env
    load_dotenv()

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    import models

    # blueprint
    import views.views as views
    app.register_blueprint(views.bp)
    
    return app