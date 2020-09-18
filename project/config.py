# default configuration
import os
ENV = os.getenv("FLASK_ENV")
# DEBUG = ENV == "development"
# SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY = 'secret-key-goes-here'

# SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'

# CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
# CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
