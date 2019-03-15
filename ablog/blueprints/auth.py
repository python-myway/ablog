from datetime import datetime
from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from ablog.forms import LoginForm, SignupForm, ForgetPasswordForm, ResetPasswordForm
from ablog.models import db, User
from ablog.utils import redirect_back, validate_token, generate_token, confirm_email_notice
from ablog.mails import send_confirm_email, send_change_email_email, send_reset_password_email

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
            flash('Login seccussfully, enjoy your day.', 'info')
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
        token = generate_token(user=user, operation='CONFIRM')
        send_confirm_email(user=user, token=token)
        confirm_email_notice(url_for('auth.confirm', token=token), user)
        flash('Confirm email sent, Please check your inbox.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html', form=form)


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('post.home'))

    if validate_token(user=current_user, token=token, operation='CONFIRM'):
        flash('Account confirmed.', 'success')
        return redirect(url_for('post.home'))
    else:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('auth.resend_confirm_email'))


@auth_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for('post.home'))

    token = generate_token(user=current_user, operation='CONFIRM')
    send_confirm_email(user=current_user, token=token)
    flash('New email sent, Please check your inbox.', 'info')
    return redirect(url_for('post.home'))


@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('post.home'))

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_token(user=user, operation='RESET_PASSWORD')
            send_reset_password_email(user=user, token=token)
            flash('Password reset email sent, Please check your inbox.', 'info')
            return redirect(url_for('auth.login'))
        flash('Invalid email.', 'warning')
        return redirect(url_for('auth.forget_password'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('post.home'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('.index'))
        if validate_token(user=user, token=token, operation='RESET_PASSWORD',
                          new_password=form.password.data):
            flash('Password updated.', 'success')
            return redirect(url_for('.login'))
        else:
            flash('Invalid or expired link.', 'danger')
            return redirect(url_for('auth.forget_password'))
    return render_template('auth/reset_password.html', form=form)

