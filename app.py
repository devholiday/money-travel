from flask import Flask, render_template
import mysql.connector
import os

app = Flask(__name__)

config = {
  'user': os.environ.get("DB_USER"),
  'password': os.environ.get("DB_PASSWORD"),
  'host': os.environ.get("DB_HOST"),
  'database': os.environ.get("DB_NAME"),
  'raise_on_warnings': True,
}

link = mysql.connector.connect(**config)

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
def detailBankNote(id):
    return render_template('banknote.html', id=id)

@app.route("/add")
def AddDetailBankNote():
    return render_template('add_banknote.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500