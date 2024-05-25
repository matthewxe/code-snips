from flask import Flask, request, redirect, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, func
from sqlalchemy.orm import Mapped
from flask_bcrypt import Bcrypt
from flask_login import (
    UserMixin,
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)

# LOGGING FORMAT
# def log(message, typeoflog):
def log(messages):
    escapecode = '\033[100;92mLOG ::'
    if type(messages) is list:
        for message in messages:
            print(escapecode + str(message) + '\033[0m')
    else:
        print(escapecode + str(messages) + '\033[0m')


# Supported Languages
class Lang:
    def __init__(self, name, ace, prism):
        self.name = name
        self.ace = ace
        self.prism = prism


SUPPORTED_LANGS = [
    Lang('Python', 'python', 'python'),
    Lang('HTML', 'html', 'html'),
    Lang('CSS', 'css', 'css'),
    Lang('Javascript', 'javascript', 'javascript'),
    Lang('C', 'c_cpp', 'c'),
]

# Flask Setup {{{
app = Flask(__name__)
from os import urandom

app.config['SECRET_KEY'] = urandom(24)

# Bcrypt Setup
bcrypt = Bcrypt(app)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-SQLAlchemy
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    username: Mapped[str] = db.Column(db.Text(50), unique=True, nullable=False)
    hash: Mapped[str] = db.Column(db.Text(60), nullable=False)

    def __repr__(self):
        return f'<User {self.id} {self.username}>'


class Post(db.Model):
    __tablename__ = 'post'
    post_id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    title: Mapped[str] = db.Column(db.Text(50), nullable=False)
    description: Mapped[str] = db.Column(db.Text, nullable=True)
    code: Mapped[str] = db.Column(db.Text, nullable=False)
    rating: Mapped[str] = db.Column(db.Float, nullable=False, default=0)

    def __repr__(self):
        return f'<Post {self.post_id} {self.title}>'


class Tags(db.Model):
    tag_id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    post_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    post = db.relationship('Post', backref=db.backref('post'))
    tag_content: Mapped[str] = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Tag {self.tag_id} {self.tag_content}>'


class Request(UserMixin, db.Model):
    request_id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    author_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('user'))

    title: Mapped[str] = db.Column(db.Text(50), nullable=False)
    rating: Mapped[str] = db.Column(db.Float, nullable=False, default=0)
    timetable = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Request {self.request_id} {self.title}>'


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


# }}}


@app.route('/')  # {{{
def index():
    log([User.is_active, User.is_authenticated])
    log(
        [
            User.query.all(),
            current_user.is_active,
            current_user.is_authenticated,
        ]
    )
    return render_template(
        'index.html', is_active=current_user.is_active
    )  # }}}


@app.route('/register', methods=['GET', 'POST'])  # {{{
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not username or not password or not confirm_password:
            return render_template(
                'register.html', warning='Do not leave the input blank'
            )
        elif password != confirm_password:
            return render_template(
                'register.html', warning='Passwords are not the same'
            )
        elif len(username) < 4 or len(password) < 4:
            return render_template(
                'register.html',
                warning='Username or password must be atleast 4 characters long',
            )
        elif len(username) > 50 or len(password) > 50:
            return render_template(
                'register.html',
                warning='Username or password must not be longer than 50 characters',
            )
        elif not username.isalnum():
            return render_template(
                'register.html',
                warning='Usernames must only contain English characters or numbers',
            )
        elif ' ' in password and password.isascii():
            return render_template(
                'register.html',
                warning='Usernames must only contain English characters or numbers',
            )

        username = username.lower()
        if User.query.filter_by(username=username).first():
            return render_template(
                'register.html',
                warning='That username already exists',
            )

        hash = bcrypt.generate_password_hash(password)

        db.session.add(User(username=username, hash=hash))
        db.session.commit()

        return redirect(url_for('login'))
    else:
        return render_template('register.html')  # }}}


@app.route('/login', methods=['GET', 'POST'])  # {{{
@login_manager.unauthorized_handler
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template(
                'login.html', warning='Do not leave the input blank'
            )
        username = username.lower()
        query = User.query.filter_by(username=username).first()
        if not query:
            return render_template(
                'login.html',
                warning="That user doesn't exist",
            )
        hash = query.hash
        if not bcrypt.check_password_hash(hash, password):
            return render_template('login.html', warning='Wrong password')

        login_user(query)
        return redirect(url_for('index'))
    else:
        return render_template('login.html')   # }}}


@app.route('/logout')  # {{{
def logout():
    logout_user()
    return redirect(url_for('index'))  # }}}


@app.route('/discover')  # {{{
def discover():
    return 'shithouse'  # }}}


@app.route('/create/<typeofpost>', methods=['GET', 'POST'])  # {{{
@login_required
def create(typeofpost):
    if not typeofpost:
        return redirect(url_for('index'))   # }}}

    match (typeofpost):
        case 'post':
            if request.method == 'POST':
                log(User.query.first())
                log(User.query.get(id))
                form = request.form

                for value in request.form:
                    print(value, form[value])
                return render_template(
                    'post.html',
                    is_active=current_user.is_active,
                    languages=SUPPORTED_LANGS,
                )
            else:
                return render_template(
                    'post.html',
                    is_active=current_user.is_active,
                    languages=SUPPORTED_LANGS,
                )
        case 'request':
            return render_template('post_request.html')
        case _:
            return redirect(url_for('index'))   # }}}


@app.route('/create')  # {{{
def create_menu():
    return render_template(
        'create.html',
        is_active=current_user.is_active,
    )  # }}}


if __name__ == '__main__':
    app.run()
