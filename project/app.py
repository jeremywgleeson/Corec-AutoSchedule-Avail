from flask import Flask
from .extensions import db, login_manager, bootstrap, celery
from .models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object("project.config")

    configure_extensions(app)
    register_blueprints(app)
    init_celery(app)

    with app.app_context():
        db.create_all()

    return app

def configure_extensions(app):
    db.init_app(app)

    bootstrap.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

def register_blueprints(app):
    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

def init_celery(app=None):
    app = app or create_app()
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
    celery.conf.timezone = 'US/Eastern'
    celery.conf.update(app.config)


    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
