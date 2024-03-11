from flask import Flask
from flask_wtf.csrf import CSRFProtect
from os import path

from .models import db

DB_NAME = 'db.sqlite3'
csrf_token = CSRFProtect()


app = Flask(__name__)

def create_interface():

    app.config['SECRET_KEY'] = '9fh294fh2938'
    app.config['WTF_CSRF_SECRET_KEY'] = "Your_wfk_csrf_secret_string"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQALCHEMY_TRACK_MODIFICATIONS'] = False
    app.static_folder = 'static'
    app.static_url_path = 'static'


    from .views import views


    app.register_blueprint(views, url_prefix='/')

    db.init_app(app)
    csrf_token.init_app(app)

    from . import models
    create_database(app)
    return app


def create_database(app):
    if not path.exists('instance/' + DB_NAME):
        with app.app_context():
            db.create_all()