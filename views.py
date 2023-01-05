from app import app
from flask import render_template, request, redirect, abort, url_for
import glob
import json
import locale
from forms.banknote import BanknoteForm
from forms.comment import CommentForm
from forms.search import SearchForm
import db

language_dict = []
languages = {}
default_lang = locale.getlocale()[0].split('_')[0]
language_list = glob.glob("language/*.json")
for lang in language_list:
    filename = lang.split('\\')
    lang_code = filename[1].split('.')[0]
    language_dict.append(lang_code)
    with open(lang, encoding='utf8') as file:
        languages[lang_code] = json.load(file)


f = open('./data/currencies.json', encoding="utf8")
currencies = json.load(f)
f.close()

@app.before_request
def before_request():
    try:
        path = request.full_path.rstrip('/ ?')
        ar_path = path.split('/')

        if request.url_rule and '<language>' in request.url_rule.rule:
            if len(ar_path) > 1 and (ar_path[1] not in language_dict):
                abort(404)
    except:
        abort(404)

@app.route("/", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>", methods=['GET', 'POST'])
def index(language):    
    form = SearchForm()
    form.filter.choices = [('number', languages[language]['number']), ('denomination', languages[language]['denomination']), ('ISO_code', languages[language]['currency'])]
    if form.validate_on_submit():
        records = db.fetchall_sql("select * from banknotes where " + form.filter.data + " LIKE '" + form.q.data+"%' ORDER BY id DESC")
    else:
        records = db.fetchall_sql("select * from banknotes ORDER BY id DESC")

    return render_template('index.html', form=form, **languages[language], banknotes=records, language=language)

@app.route("/b/<id>", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>/b/<id>", methods=['GET', 'POST'])
def detail_banknote(language, id):
    record = db.fetchone_sql("select * from banknotes where id="+id)
    comments = db.fetchall_sql("select * from comments where banknote_id="+str(record[0])+" ORDER BY id DESC")

    form = CommentForm()
    form.city.label = languages[language]['city']
    form.address.label = languages[language]['address']
    form.text.label = languages[language]['text']

    if form.validate_on_submit():
        db.insert_sql("""INSERT INTO comments (banknote_id, city, address, text) 
                            VALUES ('{0}', '{1}', '{2}', '{3}') """.format(id, form.city.data, form.address.data, form.text.data))
        return redirect('/')

    return render_template('banknote.html', form=form,  **languages[language], banknote=record, comments=comments)

@app.route("/add", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>/add", methods=['GET', 'POST'])
def add_banknote(language):
    form = BanknoteForm()
    form.iso_code.choices = [(g['code'], g['name'][language]) for g in currencies]
    form.iso_code.label = languages[language]['currency']
    form.number.label = languages[language]['number']
    form.denomination.label = languages[language]['denomination']
    form.city.label = languages[language]['city']
    form.address.label = languages[language]['address']
    form.text.label = languages[language]['text']
    
    if form.validate_on_submit():
        lastrowid = db.insert_sql("""INSERT INTO banknotes (ISO_code, number, denomination) 
                           VALUES ('{0}', '{1}', {2}) """.format(form.iso_code.data, form.number.data, form.denomination.data))
        db.insert_sql("""INSERT INTO comments (banknote_id, city, address, text) 
                            VALUES ('{0}', '{1}', '{2}', '{3}') """.format(lastrowid, form.city.data, form.address.data, form.text.data))
        return redirect('/')

    return render_template('add_banknote.html', form=form, **languages[language])

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500