try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app
from ablog.models import User


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