import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from ablog import db
from ablog.models import User, Category, Post, Comment

fake = Faker()


def fake_user(count=5):
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
    category = Category(name='Default')
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