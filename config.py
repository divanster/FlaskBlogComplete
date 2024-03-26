import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or 1
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['pythonflaskproject@gmail.com']



    SESSION_COOKIE_SAMESITE = 'None'  # Set SameSite attribute to None
    SESSION_COOKIE_SECURE = True  # Set secure flag for HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Set HttpOnly flag for better security
    POSTS_PER_PAGE = 5
