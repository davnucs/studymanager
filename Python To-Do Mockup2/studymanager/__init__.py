from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import text
import logging  # Added for error logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studymanager.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = None

# Enable logging for errors
logging.basicConfig(level=logging.ERROR)

from . import auth, views

with app.app_context():
    db.create_all()
    db.session.execute(text("PRAGMA foreign_keys=ON"))
    db.session.commit()