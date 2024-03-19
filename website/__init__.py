from builtins import int, print

from flask import Flask, render_template, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_login import LoginManager, current_user
from os import path
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
import logging
from logging.handlers import RotatingFileHandler
import os
from config import Config
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv

# from utilities import get_local_time  # <--- Import the function

# db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'FlaskProject', 'instance'))
# db_path = os.path.join(db_dir, 'database.db')

metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_`%(constraint_name)s`",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

db = SQLAlchemy(metadata=metadata)
DB_NAME = "database.db"
migrate = Migrate()
bootstrap = Bootstrap5()
ckeditor = CKEditor()
mail = Mail()


def create_app(config_class=Config):
    load_dotenv()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    # app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    ckeditor.init_app(app)

    # Register the get_local_time filter here
    # app.jinja_env.filters['get_local_time'] = get_local_time

    from website.errors.handlers import bp as errors_bp
    app.register_blueprint(errors_bp)

    from website.auth.auth import auth
    app.register_blueprint(auth, url_prefix='/')

    from website.views.views import views
    app.register_blueprint(views, url_prefix='/')

    from .models import User, BlogPost, Comment, Like

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app


def create_database():
    if not path.exists('website/' + DB_NAME):
        db.create_all()
        print('Created Database!')


from website import models
