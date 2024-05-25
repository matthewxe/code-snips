from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

# Flask Setup {{{
app = Flask(__name__)
from os import urandom

app.config['SECRET_KEY'] = urandom(24)
# Bcrypt Setup
bcrypt = Bcrypt(app)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f'<User {self.id} {self.username}>'


class Yell(db.Model):
    __tablename__ = 'yell'
    yell_id = db.Column(db.Integer, primary_key=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('author'))
    yell_title = db.Column(db.String(100), nullable=False)
    yell_rating = db.Column(db.Float, nullable=False, default=0)
    yell_type = db.Column(db.String(3), nullable=False)
    yell_datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow()
    )

    def __repr__(self):
        return f'<Yell {self.yell_id} {self.yell_title}>'


class Post(db.Model):
    post_content_id = db.Column(db.Integer, primary_key=True, nullable=False)
    original_yell_id = db.Column(
        db.Integer, db.ForeignKey('yell.yell_id'), nullable=False
    )
    post_description = db.Column(db.String(1000), nullable=False)
    post_code = db.Column(db.Text, nullable=False)
    post_filename = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Post id: {self.post_content_id} original: {self.original_yell_id} content: {self.post_filename}>'


class Request(db.Model):
    request_content_id = db.Column(
        db.Integer, primary_key=True, nullable=False
    )
    original_yell_id = db.Column(
        db.Integer, db.ForeignKey('yell.yell_id'), nullable=False
    )
    request_content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Request id: {self.request_content_id} original: {self.original_yell_id} content: {self.request_content}>'


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    original_yell_id = db.Column(
        db.Integer, db.ForeignKey('yell.yell_id'), nullable=False
    )
    comment_content = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Comment id: {self.comment_id} original: {self.original_yell_id} content: {self.comment_content}>'


class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    original_yell_id = db.Column(
        db.Integer, db.ForeignKey('yell.yell_id'), nullable=False
    )
    tag_content = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Tag id: {self.tag_id} original: {self.original_yell_id} content: {self.tag_content}>'


with app.app_context():
    db.create_all()
# }}}


def insert_random(db, max):  # {{{
    import random, string

    def randomword(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    for i in range(max):
        # print(i)

        fake_user = i
        # fake_user = random.randint(0, max)
        db.session.add(
            User(
                id=fake_user,
                username=randomword(50),
                # hash=bcrypt.generate_password_hash(randomword(50)),
                hash=randomword(50),
            )
        )
        db.session.add(
            Yell(
                yell_id=i,
                yell_author_id=fake_user,
                yell_title=randomword(50),
                yell_description=randomword(500),
                yell_code=randomword(1000),
                yell_filename=randomword(15),
            )
        )

    db.session.commit()


with app.app_context():
    insert_random(db, 10000)
