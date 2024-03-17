import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')

    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@example.com'
    MAIL_PASSWORD = 'your-email-password'

    SESSION_COOKIE_SAMESITE = 'None'  # Set SameSite attribute to None
    SESSION_COOKIE_SECURE = True  # Set secure flag for HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Set HttpOnly flag for better security
