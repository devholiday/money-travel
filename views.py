from app import app
from flask import render_template, request, redirect
import json
from forms.banknote import BanknoteForm

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
    f = open('./data/currencies.json', encoding="utf8")
    currencies = json.load(f)
    f.close()

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