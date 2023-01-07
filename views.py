from app import app
from flask import render_template, request, redirect, abort, session, url_for, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
import glob
import json
import locale
from forms.banknote0 import Banknote0Form
from forms.banknote import BanknoteForm
from forms.comment import CommentForm
from forms.search import SearchForm
from forms.login import LoginForm
import db
from datetime import datetime

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
        ar_path = path.split('?')[0].split('/')

        if request.url_rule and '<language>' in request.url_rule.rule:
            if len(ar_path) > 1 and (ar_path[1] not in language_dict):
                abort(404)
        
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = db.fetchone_sql("select * from users where id='"+str(user_id)+"'")
    except:
        abort(404)

@app.route("/", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>", methods=['GET', 'POST'])
def index(language):
    args = request.args.to_dict()
    type = args.get('type')

    if 'username' in session:
        print(f'Logged in as {session["username"]}')
    else:
        print('You are not logged in')

    form = SearchForm()
    form.filter.choices = [('number', languages[language]['number']), ('denomination', languages[language]['denomination']), ('ISO_code', languages[language]['currency'])]
    
    order_by = "created_at desc"
    if args.get('created_at'):
        order_by = "created_at " + args.get('created_at')

    if type == 'comments':
        top_list = db.fetchall_sql("select * from comments where enabled=1 ORDER BY " + order_by + " LIMIT 25")
    else:
        if args.get('updated_at'):
            order_by = "updated_at " + args.get('updated_at')

        top_list = db.fetchall_sql("select * from banknotes ORDER BY " + order_by + " LIMIT 25")

    return render_template('index.html', form=form, **languages[language], top_list=top_list, language=language, type=type)


@app.route("/search", defaults={'language': default_lang}, methods=['GET'])
@app.route("/<language>/search", methods=['GET'])
def search(language):
    args = request.args.to_dict()
    records = []
    form = SearchForm()
    form.filter.choices = [('number', languages[language]['number']), ('denomination', languages[language]['denomination']), ('ISO_code', languages[language]['currency'])]
    if args.get('filter') and args.get('q'):
        records = db.fetchall_sql("select * from banknotes where " + args.get('filter') + " LIKE '" + args.get('q') +"%' ORDER BY id DESC LIMIT 50")
    return render_template('search.html', form=form, **languages[language], banknotes=records, language=language, q=args.get('q'))


@app.route("/b/<id>", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>/b/<id>", methods=['GET', 'POST'])
def detail_banknote(language, id):
    record = db.fetchone_sql("select * from banknotes where id="+id)
    comments = db.fetchall_sql("select * from comments where banknote_id="+str(record[0])+" ORDER BY id DESC LIMIT 30")

    form = CommentForm()
    form.city.label = languages[language]['city']
    form.address.label = languages[language]['address']
    form.text.label = languages[language]['text']

    if form.validate_on_submit():
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        db.update_sql("""Update banknotes set updated_at='{0}' where id={1}""".format(formatted_date, id))
        db.insert_sql("""INSERT INTO comments (banknote_id, city, address, text) 
                            VALUES ('{0}', '{1}', '{2}', '{3}') """.format(id, form.city.data, form.address.data, form.text.data))
        return redirect('/')

    return render_template('banknote.html', form=form,  **languages[language], banknote=record, comments=comments)


@app.route("/add", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>/add", methods=['GET', 'POST'])
def add_banknote(language):
    args = request.args.to_dict()
    step = args.get('step')
    banknote_id = args.get('banknote_id')
    
    if step is None or step == '1':
        form = Banknote0Form()
        form.iso_code.choices = [(g['code'], g['name'][language]) for g in currencies]
        form.iso_code.label = languages[language]['currency']
        form.number.label = languages[language]['number']
    elif step == '2':
        form = BanknoteForm()
        form.denomination.label = languages[language]['denomination']
        form.city.label = languages[language]['city']
        form.address.label = languages[language]['address']
        form.text.label = languages[language]['text']
    
    if form.validate_on_submit():
        if step is None or step == '1':
            banknote = db.fetchone_sql("select * from banknotes where iso_code='"+form.iso_code.data+"' and number='"+form.number.data+"'")
            if banknote is None:
                lastrowid = db.insert_sql("""INSERT INTO banknotes (ISO_code, number) 
                        VALUES ('{0}', '{1}') """.format(form.iso_code.data, form.number.data))
                return redirect(url_for('add_banknote', language=language, step=2, banknote_id=lastrowid))
            else:
                return redirect(url_for('add_banknote', language=language, step=2, banknote_id=banknote[0]))

        if step == '2':
            if banknote_id is not None:
                now = datetime.now()
                formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                db.update_sql("""Update banknotes set denomination='{0}', updated_at='{1}' where id={2}""".format(form.denomination.data, formatted_date, banknote_id))
                db.insert_sql("""INSERT INTO comments (banknote_id, city, address, text)
                        VALUES ('{0}', '{1}', '{2}', '{3}') """.format(banknote_id, form.city.data, form.address.data, form.text.data))
                return redirect('/')

    return render_template('add_banknote.html', form=form, **languages[language])


@app.route("/admin/comments", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>/admin/comments", methods=['GET', 'POST'])
def admin_comments(language):
    comments = db.fetchall_sql("select * from comments ORDER BY id DESC LIMIT 30")

    if request.method == 'POST':
        comment_id = request.form['id']
        enabled = request.form['enabled']
        db.update_sql("""Update comments set enabled='{0}' where id={1}""".format(enabled, comment_id))
        return redirect(url_for('admin_comments'))

    return render_template('admin/comments.html', **languages[language], comments=comments)


@app.route("/login", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>/login", methods=['GET', 'POST'])
def login(language):
    error = None

    form = LoginForm()
    form.username.label = languages[language]['username']
    form.password.label = languages[language]['password']
    if form.validate_on_submit():
        user = db.fetchone_sql("select * from users where username='"+form.username.data+"'")
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], form.password.data):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))

    flash(error)
    return render_template('auth/login.html', form=form, **languages[language], error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500