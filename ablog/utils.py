try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from itsdangerous import BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer as Serializer
from elasticsearch import Elasticsearch
from flask import request, redirect, url_for, current_app

from ablog.models import db, User, Notice

ela_client = Elasticsearch()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='post.home', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ABLOG_ALLOWED_IMAGE_EXTENSIONS']


def be_active(value, pattern='new'):
    value = value.split('.')[-1]
    if pattern in str(value):
        return True
    return False


def is_follow(value, username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    if value.is_following(user):
        return True
    return False


def add_follow_notice(follower, receiver):
    message = 'User <a href="%s">%s</a> followed you.' % \
              (url_for('user.user', user_id=follower.id), follower.username)
    notice = Notice(message=message, receiver=receiver)
    db.session.add(notice)
    db.session.commit()


def add_comment_notice(post_id, receiver, page=1):
    message = '<a href="%s#comments">This post</a> has new comment/reply.' % \
              (url_for('post.show_post', post_id=post_id, page=page))
    notice = Notice(message=message, receiver=receiver)
    db.session.add(notice)
    db.session.commit()


def add_post_notice(following, post_id, receiver):
    message = 'User <a href="%s">%s</a> published a new <a href="%s">post.</a>' % \
              (url_for('user.user', user_id=following.id),
               following.username,
               url_for('post.show_post', post_id=post_id))
    notice = Notice(message=message, receiver=receiver)
    db.session.add(notice)
    db.session.commit()


def confirm_email_notice(receiver):
    message = 'Confirm email sent, Please check your inbox'
    notice = Notice(message=message, receiver=receiver)
    db.session.add(notice)
    db.session.commit()


def generate_token(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == 'CONFIRM':
        user.confirmed = True
    elif operation == 'RESET_PASSWORD':
        user.password(new_password)
    elif operation == 'CHANGE_EMAIL':
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True