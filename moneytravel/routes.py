from flask import render_template, request, redirect, abort, session, url_for, flash, g
from moneytravel import app, db
from werkzeug.security import check_password_hash
import glob
import json
import locale
from datetime import datetime

from moneytravel.forms.banknote0 import Banknote0Form
from moneytravel.forms.banknote import BanknoteForm
from moneytravel.forms.comment import CommentForm
from moneytravel.forms.search import SearchForm
from moneytravel.forms.login import LoginForm

from moneytravel.models import User, Banknote, Comment

language_dict = []
languages = {}
default_lang = locale.getlocale()[0].split('_')[0]
language_list = glob.glob("moneytravel/language/*.json")
for lang in language_list:
    filename = lang.split('\\')
    lang_code = filename[1].split('.')[0]
    language_dict.append(lang_code)
    with open(lang, encoding='utf8') as file:
        languages[lang_code] = json.load(file)


f = open('./moneytravel/data/currencies.json', encoding="utf8")
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
            g.user = User.query.get_or_404(user_id)
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
    form.filter.choices = [('number', languages[language]['number']), ('denomination', languages[language]['denomination']), ('iso_code', languages[language]['currency'])]
    
    if type == 'comments':
        order_by = Comment.created_at.desc()
        if args.get('created_at'):
            order_by = Comment.created_at.desc() if args.get('created_at') == 'desc' else Comment.created_at.asc()
        top_list = Comment.query.filter_by(enabled=True).order_by(order_by).limit(25).all()
    else:
        order_by = Banknote.created_at.desc()
        if args.get('created_at'):
            order_by = Banknote.created_at.desc() if args.get('created_at') == 'desc' else Banknote.created_at.asc()
        if args.get('updated_at'):
            order_by = Banknote.updated_at.desc() if args.get('updated_at') == 'desc' else Banknote.updated_at.asc()
        top_list = Banknote.query.order_by(order_by).limit(25).all()

    return render_template('index.html', form=form, **languages[language], top_list=top_list, language=language, type=type)


@app.route("/search", defaults={'language': default_lang}, methods=['GET'])
@app.route("/<language>/search", methods=['GET'])
def search(language):
    args = request.args.to_dict()
    banknotes = []
    form = SearchForm()
    form.filter.choices = [('number', languages[language]['number']), ('denomination', languages[language]['denomination']), ('iso_code', languages[language]['currency'])]
    if args.get('filter') and args.get('q'):
        search = "{}%".format(args.get('q'))
        filter_by = Banknote.iso_code.like(search)
        if (args.get('filter') == 'number'):
            filter_by = Banknote.number.like(search)
        if (args.get('filter') == 'denomination'):
            filter_by = Banknote.denomination.like(search)
        banknotes = Banknote.query.filter(filter_by).order_by(Banknote.id.desc()).limit(50).all()

    return render_template('search.html', form=form, **languages[language], banknotes=banknotes, language=language, q=args.get('q'))


@app.route("/b/<id>", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>/b/<id>", methods=['GET', 'POST'])
def detail_banknote(language, id):
    banknote = Banknote.query.get_or_404(id)
    comments = Comment.query.filter_by(banknote_id=id, enabled=True).order_by(Comment.id.desc()).limit(30).all()

    form = CommentForm()
    form.city.label = languages[language]['city']
    form.address.label = languages[language]['address']
    form.text.label = languages[language]['text']

    if form.validate_on_submit():    
        banknote = Banknote.query.get_or_404(id)
        banknote.updated_at = datetime.utcnow()

        new_comment = Comment(banknote_id=id, city=form.city.data, address=form.address.data, text=form.text.data)
        db.session.add(new_comment)

        db.session.commit()

        return redirect('/')

    return render_template('banknote.html', form=form,  **languages[language], banknote=banknote, comments=comments)


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
            banknote = Banknote.query.filter_by(iso_code = form.iso_code.data, number = form.number.data).one_or_none()
            if banknote is None:
                new_banknote = Banknote(iso_code=form.iso_code.data, number=form.number.data)
                db.session.add(new_banknote)
                db.session.commit()
                return redirect(url_for('add_banknote', language=language, step=2, banknote_id=new_banknote.id))
            else:
                return redirect(url_for('add_banknote', language=language, step=2, banknote_id=banknote.id))

        if step == '2':
            if banknote_id is not None:
                banknote = Banknote.query.get_or_404(banknote_id)
                banknote.denomination = form.denomination.data
                banknote.updated_at = datetime.utcnow()
                
                new_comment = Comment(banknote_id=banknote_id, city=form.city.data, address=form.address.data, text=form.text.data)
                db.session.add(new_comment)

                db.session.commit()

                return redirect('/')

    return render_template('add_banknote.html', form=form, **languages[language])


@app.route("/admin/comments", defaults={'language': default_lang}, methods=['GET', 'POST'])
@app.route("/<language>/admin/comments", methods=['GET', 'POST'])
def admin_comments(language):
    comments = Comment.query.order_by(Comment.id.desc()).limit(30).all()

    if request.method == 'POST':
        comment_id = request.form['id']
        enabled = request.form['enabled']
        
        comment = Comment.query.get_or_404(comment_id)
        comment.enabled = bool(int(enabled))
        db.session.commit()

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
        user = User.query.filter_by(username = form.username.data).one_or_none()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, form.password.data):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
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