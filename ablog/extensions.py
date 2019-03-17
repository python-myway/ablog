from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
# from celery import Celery
from flask_whooshee import Whooshee


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
mail = Mail()
moment = Moment()
toolbar = DebugToolbarExtension()
migrate = Migrate()
# celery_app = Celery()
whooshee = Whooshee()


@login_manager.user_loader
def load_user(id):
    from ablog.models import User
    user = User.query.get(id)
    return user


login_manager.login_view = 'index'
login_manager.login_message_category = 'warning'
