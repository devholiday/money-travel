from flask import Flask
import os
import locale

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app.url_map.strict_slashes = False

locale.setlocale(locale.LC_ALL, 'ru')

import views