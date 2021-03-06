import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from ablog import db
from ablog.models import User, Category, Post, Comment, ElaPost
from ablog.utils import ela_client


fake = Faker()


def fake_user(count=5):
    super_admin = User(username='superadmin', 
            email='superadmin@super163.com', 
            password='superadmin')
    db.session.add(super_admin)
    db.session.commit()
    for i in range(count):
        admin = User(
            username='admin{}'.format(str(i)),
            email='admin{}@163.com'.format(str(i)),
            password='admin{}'.format(str(i)),
        )
        db.session.add(admin)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def fake_categories(count=10):
    super_admin = User.query.filter_by(username='superadmin').first()
    category = Category(name='default', author=super_admin)
    db.session.add(category)
    for _ in range(count):
        category = Category(name=fake.word(), author=User.query.get(random.randint(1, User.query.count())))
        db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def fake_posts(count=50):
    for _ in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year(),
            author=User.query.get(random.randint(1, User.query.count())),
        )
        db.session.add(post)
        elapost = ElaPost(meta={'id': post.id}, title=post.title, body=post.body)
        elapost.save(using=ela_client)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def fake_comments(count=50):
    for _ in range(count):
        comment = Comment(
            author=User.query.get(random.randint(1, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        comment = Comment(
            author=User.query.get(random.randint(1, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()