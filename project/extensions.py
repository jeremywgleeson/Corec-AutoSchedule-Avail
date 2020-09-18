# all extensions used and initialized stored here
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from celery import Celery

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
celery = Celery()
