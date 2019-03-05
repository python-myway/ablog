import os

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail

from ablog.forms import PostForm
from ablog.models import db, Post, Category, Comment, User
from ablog.utils import redirect_back, allowed_file

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/<int:user_id>')
@login_required
def user(user_id):
    author = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page=current_app.config['ABLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(author)\
            .order_by(Post.timestamp.desc())\
            .paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('user/user.html', user=author, posts=posts,
                           pagination=pagination)


@user_bp.route('/follow/<int:user_id>')
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_following(user):
        flash('You are already following this user.', 'warning')
        return redirect_back()
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}.'.format(user.username), 'success')
    return redirect_back()


@user_bp.route('/unfollow/<int:user_id>')
@login_required
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_following(user):
        flash('You are not following this user.', 'warning')
        return redirect_back()
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {} anymore.'.format(user.username), 'success')
    return redirect_back()

@user_bp.route('/followers/<int:user_id>')
@login_required
def followers(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    pagination = user.follower.paginate(
        page, per_page=current_app.config['ABLOG_TABLE_PER_PAGE'])
    return render_template('user/followers.html', 
            user=user, pagination=pagination, page=page, 
            followers=pagination.items, title='Followers')


@user_bp.route('/followed_by/<int:user_id>')
@login_required
def followed_by(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['ABLOG_TABLE_PER_PAGE'])
    return render_template('user/followers.html', 
            user=user, pagination=pagination, page=page,
            followers=pagination.items, title="Followed by")