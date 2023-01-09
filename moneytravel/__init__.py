from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import locale

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.url_map.strict_slashes = False

db = SQLAlchemy(app)

locale.setlocale(locale.LC_ALL, 'ru')

from moneytravel import routes