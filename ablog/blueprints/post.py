from flask import (render_template, flash, redirect, url_for, request, 
                    current_app, Blueprint, abort, make_response)
from flask_login import current_user, login_required

from ablog.forms import CommentForm, SearchForm, PostForm, CategoryForm
from ablog.models import db, Post, Category, Comment, Follow
from ablog.utils import redirect_back

post_bp = Blueprint('post', __name__)


@post_bp.route('/home')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ABLOG_POST_PER_PAGE']
    pagination = Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == current_user.id)\
            .order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('post/home.html', pagination=pagination, posts=posts)


@post_bp.route('/search', methods=['POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search = form.search.data
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['ABLOG_POST_PER_PAGE']
        pagination = Post.query.filter(Post.body.ilike('%{}%'.format(search)))\
                .order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
        posts = pagination.items
        return redirect(url_for('post.search', pagination=pagination, posts=posts))
    return render_template('post/search.html')


@post_bp.route('/category/<int:category_id>')
@login_required
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ABLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category)\
            .order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('post/category.html', category=category, pagination=pagination, posts=posts)


@post_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ABLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post)\
            .order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items

    form = CommentForm()
    if form.validate_on_submit():
        body = form.body.data
        comment = Comment(author=current_user, body=body, post=post)
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
        db.session.add(comment)
        db.session.commit()
        flash('Comment published.', 'success')
        return redirect(url_for('post.show_post', post_id=post_id))
    return render_template('post/post.html', post=post, pagination=pagination, form=form, comments=comments)


@post_bp.route('/reply/comment/<int:comment_id>')
@login_required
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        # just in case
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('post.show_post', post_id=comment.post.id))
    return redirect(
        url_for('post.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author.username) + '#comment-form')


@post_bp.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(author_id=current_user.id)\
            .order_by(Post.timestamp.desc())\
            .paginate(page, per_page=current_app.config['ABLOG_TABLE_PER_PAGE'])
    posts = pagination.items
    return render_template('post/manage_post.html', page=page, pagination=pagination, posts=posts)


@post_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        author_id = current_user.id
        category = Category.query.get(form.category.data)
        post = Post(title=title, body=body, category=category, author_id=author_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('post.show_post', post_id=post.id))
    return render_template('post/new_post.html', form=form)


@post_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('post.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('post/edit_post.html', form=form)


@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()


@post_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()


@post_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()


@post_bp.route('/category/manage')
@login_required
def manage_category():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ABLOG_TABLE_PER_PAGE']
    pagination = Category.query.filter_by(author_id=current_user.id)\
            .paginate(page, per_page=per_page)
    categories = pagination.items
    return render_template('post/manage_category.html', page=page, pagination=pagination, categories=categories)


@post_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        author = current_user
        category = Category(name=name, author=author)
        db.session.add(category)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('post.manage_category'))
    return render_template('post/new_category.html', form=form)


@post_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not edit the default category.', 'warning')
        return redirect(url_for('post.home'))
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('post.manage_category'))
    form.name.data = category.name
    return render_template('post/edit_category.html', form=form)


@post_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not delete the default category.', 'warning')
        return redirect(url_for('post.home'))
    category.delete()
    flash('Category deleted.', 'success')
    return redirect(url_for('post.manage_category'))


@post_bp.route('/uploads/<path:filename>')
@login_required
def get_image(filename):
    return send_from_directory(current_app.config['ABLOG_UPLOAD_PATH'], filename)


@post_bp.route('/upload', methods=['POST'])
@login_required
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('Image only!')
    f.save(os.path.join(current_app.config['ABLOG_UPLOAD_PATH'], f.filename))
    url = url_for('post.get_image', filename=f.filename)
    return upload_success(url, f.filename)
