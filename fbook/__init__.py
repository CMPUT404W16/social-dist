from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.pagedown import PageDown

from admin import configureAdmin
from .db import db

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
pagedown = PageDown()

def create_app(conf):
    app = Flask(__name__)
    app.config.from_object(conf)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)

    from api.api import api
    api.init_app(app)

    configureAdmin(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

