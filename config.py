import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = '!@#secure!@#Key321'
SQLALCHEMY_POOL_RECYCLE = 3600

# email server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'webstore1092@gmail.com'
MAIL_PASSWORD = 'test123456789'
ADMINS = ['webstore1092@gmail.com']

try:
    from local_config import *
except ImportError:
    pass

