import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from datetime import timedelta


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

mail = Mail(app)

app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=15)

admin_login = LoginManager()
admin_login.init_app(app)
admin_login.login_view = 'admin_login'


@admin_login.user_loader
def load_user(id):
    return Admin.query.get(int(id))


from app import views, models
from models import User, Admin