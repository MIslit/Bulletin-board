import os
from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit

from urllib3 import Retry
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.models import User, Ad, Category
from app.forms import LoginForm, RegistrationForm, PlaceOnAd, Buy


@app.route('/place_on_ad/', methods=['GET', 'POST'])
@login_required
def place_on_ad():
    form = PlaceOnAd()
    image = form.image.data
    select = request.form.get('category_form')
    category = Category.query.all()
    selected_category = form.category.data
    if form.validate_on_submit():
        user = db.first_or_404(
            sa.select(User).where(User.username == current_user.username))
        selected_category = db.first_or_404(
            sa.select(Category).where(Category.name == selected_category))
        ad = Ad(title=form.title.data, text=form.text.data, 
                author=user, category=selected_category, price=form.price.data)
        db.session.add(ad)
        db.session.commit()
        file = request.files['image']
        if file:
            new_filename = f"{db.session.query(ad.id).first()[0]}.jpg"
            file.save(os.path.join(app.root_path, 'static', new_filename))
        flash('Вы разместили объявление!')  
        return redirect(url_for('place_on_ad'))
    return render_template('place_on_ad.html', category=category, image=image, select=select,
                            form=form)


@app.route('/ad/<id>/')
def current_ad(id):
    ad = db.first_or_404(sa.select(Ad).where(Ad.id == id))
    author = ad.author.username
    user = db.first_or_404(sa.select(User).where(User.username == author))
    image = f"/static/{id}.jpg"
    category = Category.query.all()
    form = Buy()
    return render_template('current_ad.html', ad=ad, user=user, image=image, 
                           category=category, form=form)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    category = Category.query.all()
    query = sa.select(Ad).order_by(Ad.timestamp.desc())
    ads = db.paginate(query, page=1, error_out=False)
    image = "/static/"     
    path = request.path    
    if request.method == 'POST':
        search = request.form['search']
        return search_results(search) 
    
    return render_template('index.html', title='Главная страница', 
                           category=category, ads=ads, image=image, 
                           path=path)


@app.route('/results')
def search_results(search):
    image = "/static/"   
    if search:
        query = db.session.query(Ad).where(Ad.title.like(f"%{search.lower()}%")).order_by(
            Ad.timestamp.desc())
        ads = db.paginate(query, page=1, error_out=False)
        results = query.all()

    if not results:
        flash('Нет результатов по данному запросу.')
        return redirect(url_for('index'))
    else:
        return render_template('results.html', results=results, ads=ads,
                               image=image, search=search)


@app.route('/category/<category>')
def category(category):
    selected_category = db.first_or_404(sa.select(Category).where(Category.name == category))
    query = sa.select(Ad).where(Ad.category == selected_category).order_by(Ad.timestamp.desc())
    ads = db.paginate(query, page=1, error_out=False)
    all_categories = Category.query.all()
    image = "/static/"
    path = request.path
    return render_template('category.html', category=all_categories, 
                           image=image, ads=ads, path=path)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

