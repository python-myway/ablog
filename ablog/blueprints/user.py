import os

from flask import (render_template, flash, redirect, url_for, 
	request, current_app, Blueprint, send_from_directory, jsonify)
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail
from sqlalchemy.sql import func, desc

from ablog.forms import PostForm
from ablog.models import db, Post, Category, Comment, User, Notice
from ablog.utils import redirect_back, allowed_file, add_follow_notice

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/<int:user_id>')
@login_required
def user(user_id):
	author = User.query.get_or_404(user_id)
	page = request.args.get('page', 1, type=int)

	per_page_posts=current_app.config['ABLOG_POST_PER_PAGE']
	pagination_posts = Post.query.with_parent(author)\
			.order_by(Post.timestamp.desc())\
			.paginate(page, per_page=per_page_posts)
	posts = pagination_posts.items
	followers = []
	pagination_followers= [] 
	pagination_followings= [] 
	followings = []

	per_page_followers = current_app.config['ABLOG_TABLE_PER_PAGE']
	pagination_followers = author.follower.paginate(1, per_page=per_page_followers)
	followers = pagination_followers.items

	per_page_followings = current_app.config['ABLOG_TABLE_PER_PAGE']
	pagination_followings = author.followed.paginate(1, per_page=per_page_followings)
	followings = pagination_followings.items

	return render_template('user/user.html', page=page, user=author, 
		posts=posts, pagination_posts=pagination_posts, 
		followers=followers, pagination_followers=pagination_followers, 
		followings=followings, pagination_followings=pagination_followings)

	
@user_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
	user = User.query.get_or_404(user_id)
	if current_user.is_following(user):
		flash('You are already following this user.', 'warning')
		return redirect_back()
	current_user.follow(user)
	add_follow_notice(current_user._get_current_object(), user)
	db.session.commit()
	flash('You are now following {}.'.format(user.username), 'success')
	return redirect_back()


@user_bp.route('/unfollow/<int:user_id>', methods=['POST'])
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


@user_bp.route('/recommend')
@login_required
def recommend():
		# just for now
		stmt = db.session.query(Comment.post_id, func.count('*').\
				label('comment_count')).group_by(Comment.post_id).subquery()
		raw_hotest = db.session.query(Post, stmt.c.comment_count).\
				outerjoin(stmt, Post.id==stmt.c.post_id).\
				order_by(desc(stmt.c.comment_count)).limit(5).all()
		posts_hotest_user = set([post.author for (post, _) in raw_hotest \
				if post.author.id != current_user._get_current_object().id])
		return render_template('user/recommend.html', users=posts_hotest_user)


@user_bp.route('/notices')
@login_required
def show_notices():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ABLOG_NOTICE_PER_PAGE']
    notices = Notice.query.with_parent(current_user)
    filter_ = request.args.get('filter')
    if filter_ == 'unread':
        notices = notices.filter_by(read=False)
    pagination = notices.order_by(Notice.timestamp.desc()).paginate(page, per_page)
    return render_template('user/notices.html', 
					pagination=pagination, notices=pagination.items)


@user_bp.route('/notices/read/<int:notice_id>', methods=['POST'])
@login_required
def read_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    if current_user != notice.receiver:
        abort(403)
    notice.read = True
    db.session.commit()
    flash('Notification archived.', 'success')
    return redirect(url_for('user.show_notices'))


@user_bp.route('/notices/read/all', methods=['POST'])
@login_required
def read_all_notices():
    for notice in current_user.notices:
        notice.read = True
    db.session.commit()
    flash('All notifications archived.', 'success')
    return redirect(url_for('user.show_notices'))


@user_bp.route('/ajax_notices')
@login_required
def ajax_notices():
	notices_count = Notice.query.with_parent(current_user).filter_by(read=False).count()
	return jsonify(notices_count)
