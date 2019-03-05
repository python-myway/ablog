from datetime import datetime
from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from ablog.forms import LoginForm, SignupForm
from ablog.models import db, User
from ablog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(username=username).first()
        if user and user.validate_password(password):
            login_user(user, remember)
            user.last_seen = datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            flash('Welcome back.', 'info')
            return redirect(url_for('post.home'))
        flash('Invalid username or password.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successfully.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data, 
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Signup successfully. Enjoy your day', 'info')
        return redirect(url_for('post.home'))
    return render_template('auth/signup.html', form=form)
