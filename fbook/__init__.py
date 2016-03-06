from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.pagedown import PageDown
from config import config
from flask.ext.login import LoginManager


# for login
login_manager = LoginManager()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()


def create_app(conf):
    app = Flask(__name__)
<<<<<<< HEAD:app/__init__.py

    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
=======
    app.config.from_object(conf)
    #conf.init_app(app)
>>>>>>> 74cda63a7d6ad320b8959042ffd3d040ff80cdae:fbook/__init__.py

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = '/login'
    login_manager.login_message = ""


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
