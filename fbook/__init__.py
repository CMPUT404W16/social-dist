from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.pagedown import PageDown

from flask_admin import Admin
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
admin = Admin()

def create_app(conf):
    app = Flask(__name__)
    app.config.from_object(conf)
    #conf.init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    admin.init_app(app)

    # admin.add_view(ModelView(User, db.session))

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

