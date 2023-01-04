from app import app
from flask import render_template, request, redirect, abort, url_for
import glob
import json
import locale
from forms.banknote import BanknoteForm

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

@app.before_request
def before_request():
    try:
        path = request.full_path.rstrip('/ ?')
        ar_path = path.split('/')

        if '<language>' in request.url_rule.rule:
            if len(ar_path) > 1 and (ar_path[1] not in language_dict):
                return redirect(url_for(request.endpoint, language=default_lang), 301)
    except:
        abort(404)

@app.route("/", defaults={'language': default_lang})
@app.route("/<language>")
def index(language):
    return render_template('index.html', **languages[language])

@app.route("/<language>/search")
def search(language):
    return render_template('search.html')

@app.route("/<language>/b/<id>")
def detail_banknote(language, id):
    return render_template('banknote.html', id=id)

@app.route("/add", defaults={'language': default_lang})
@app.route("/<language>/add", methods=['GET', 'POST'])
def submit(language):
    f = open('./data/currencies.json', encoding="utf8")
    currencies = json.load(f)
    f.close()

    form = BanknoteForm()
    form.iso_code.choices = [(g['code'], g['name']['en']) for g in currencies]
    if form.validate_on_submit():
        # Add to DB
        return redirect('/')

    return render_template('add_banknote.html', form=form, **languages[language])

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500