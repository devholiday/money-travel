from flask import Flask, render_template, request, redirect
import mysql.connector
import os
import json
from forms.banknote import BanknoteForm

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

config = {
  'user': os.environ.get("DB_USER"),
  'password': os.environ.get("DB_PASSWORD"),
  'host': os.environ.get("DB_HOST"),
  'database': os.environ.get("DB_NAME"),
  'raise_on_warnings': True,
}

link = mysql.connector.connect(**config)

f = open('./data/currencies.json', encoding="utf8")
currencies = json.load(f)
f.close()

if link.is_connected():
    cursor = link.cursor()
    cursor.execute("select * from banknotes;")
    record = cursor.fetchone()
    print("You're connected to database: ", record)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/search")
def search():
    return render_template('search.html')

@app.route("/b/<id>")
def detail_banknote(id):
    return render_template('banknote.html', id=id)

@app.route("/add", methods=['GET', 'POST'])
def submit():
    form = BanknoteForm()
    form.iso_code.choices = [(g['code'], g['name']['en']) for g in currencies]
    if form.validate_on_submit():
        # Add to DB
        return redirect('/')
    return render_template('add_banknote.html', form=form)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500