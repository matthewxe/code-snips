from flask import (
    Flask,
    request,
    redirect,
    render_template,
    url_for,
    jsonify,
)
from flask_login import (
    UserMixin,
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_sock import Sock
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from nh3 import clean, clean_text
from markdown import extensions, markdown
from markdown.extensions.fenced_code import FencedCodeExtension as fenced_code
from markdown.extensions.codehilite import CodeHiliteExtension as codehilite
from rapidfuzz import fuzz
from datetime import datetime
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer_for_filename
from pygments.formatters import HtmlFormatter


# Print decorators
LOG = '\033[100;92mLOG ::'
END = '\033[0m'


# Flask Setup {{{
app = Flask(__name__)
sock = Sock(app)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 7}
from os import urandom

app.config['SECRET_KEY'] = urandom(24)
# Bcrypt Setup
bcrypt = Bcrypt(app)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
# }}}

# Flask-SQLAlchemy{{{
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


class Post(db.Model):
    __tablename__ = 'post'
    yell_id = db.Column(db.Integer, primary_key=True)
    yell_maker_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False
    )
    yell_maker = db.relationship('User', backref=db.backref('yell_maker'))
    yell_title = db.Column(db.String(100), nullable=False)
    yell_description = db.Column(db.String(1000), nullable=False)
    yell_code = db.Column(db.Text, nullable=False)
    yell_filename = db.Column(db.String, nullable=False)
    yell_rating = db.Column(db.Float, nullable=False, default=0)
    yell_datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.now()
    )

    def __repr__(self):
        return f'<Post {self.yell_id} {self.yell_title}>'


class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    original_yell_id = db.Column(db.Integer, db.ForeignKey('post.yell_id'))
    original_yell = db.relationship('Post', backref=db.backref('post'))
    tag_content = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Tag {self.tag_id} {self.tag_content}>'


class Request(UserMixin, db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('author'))

    request_title = db.Column(db.String(100), nullable=False)
    request_rating = db.Column(db.Float, nullable=False, default=0)
    request_timetable = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Request {self.request_id} {self.request_title}>'


with app.app_context():
    db.create_all()
# }}}


# Other{{{
@login_manager.user_loader
def load_user(id):
    # print(LOG, User.query.get(id), id, END)
    return User.query.get(id)


@app.errorhandler(404)
def page_not_found(error):
    return redirect('/')


# }}}


@app.route('/')  # {{{
def index():
    if current_user.is_active:
        print(current_user.username, current_user.hash)
    else:
        print(current_user.is_anonymous)
    return render_template('index.html', current_user=current_user)


# }}}


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
        check = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar()
        if check:
            return render_template(
                'register.html',
                warning='That user already exists',
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
        query = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar()
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
        return render_template('login.html')


# }}}


@app.route('/logout')  # {{{
def logout():
    logout_user()
    return redirect(url_for('index'))


# }}}


@app.route('/discover')  # {{{
def discover():
    return render_template(
        'discover.html',
        current_user=current_user,
    )


# }}}


@app.route('/search')  # {{{
def search():
    # print(request.args.get('q'))
    return render_template(
        'discover.html',
        current_user=current_user,
        search=request.args.get('q'),
    )


# }}}


@app.route('/create')  # {{{
def create_menu():
    return render_template(
        'create.html',
        search=request.args.get('q'),
    )


# }}}


@app.route('/create/post', methods=['GET', 'POST'])  # {{{
@login_required
def post():
    if request.method == 'POST':
        send_error = lambda render_template, warning: render_template(
            'post.html',
            warning=warning,
            current_user=current_user,
        )
        user_id = current_user.get_id()
        if not user_id:
            return send_error(render_template, 'yuh')

        title = request.form.get('title')
        if not title:
            return send_error(render_template, 'Must provide a title.')
        description = request.form.get('description')
        if not description:
            return send_error(render_template, 'Must provide a description.')
        filename = request.form.get('filename')
        if not filename:
            return send_error(render_template, 'Must have a file name.')
        code = request.form.get('code')
        if not code:
            return send_error(render_template, 'Must provide code.')

        elif not len(title) >= 3 and not len(title) <= 100:
            return send_error(
                render_template,
                'Titles must be atleast 3 characters long and a maximum of 100',
            )
        elif not len(description) >= 3 and not len(description) <= 1000:
            return send_error(
                render_template,
                'Description must be atleast 3 characters long and a maximum of 1000',
            )

        title = clean(title)
        description = clean(
            markdown(
                description,
                extensions=[
                    codehilite(pygments_style='one-dark'),
                    fenced_code(),
                ],
            )
        )
        # code = clean_text(code)
        filename = clean_text(filename)
        print(LOG, title, description, code, filename, END)

        try:
            lexer = guess_lexer_for_filename(filename, code)
            code = highlight(
                code, lexer, HtmlFormatter(style='one-dark', lineos='table')
            )
        except:
            code = clean_text(code)

        print(LOG, code, END)
        db.session.add(
            Post(
                yell_maker_id=user_id,
                yell_title=title,
                yell_description=description,
                yell_code=code,
                yell_filename=filename,
            )
        )
        db.session.commit()

        return redirect(url_for('index'))
    else:
        return render_template(
            'post.html',
            current_user=current_user,
        )


@app.route('/create/request', methods=['GET', 'POST'])  # {{{
@login_required
def post_request():
    if request.method == 'POST':
        return render_template('post_request.html')
    else:
        return redirect(url_for('index'))


# }}}


@app.route('/yell/<yell_id>')  # {{{
def get_yell(yell_id):
    if yell_id == 'last':
        query = db.session.execute(
            db.select(Post).order_by(Post.yell_id.desc())
        ).scalar()
    else:
        query = db.session.execute(
            db.select(Post).where(Post.yell_id == yell_id)
        ).scalar()
    print(query)
    if not query:
        return '404'

    # try:
    return jsonify(
        yell_id=query.yell_id,
        yell_maker_id=query.yell_maker_id,
        yell_maker=db.session.execute(
            db.select(User).where(User.id == query.yell_maker_id)
        )
        .scalar()
        .username,
        yell_filename=query.yell_filename,
        yell_title=query.yell_title,
        yell_rating=query.yell_rating,
        yell_description=query.yell_description,
        yell_code=query.yell_code,
        yell_datetime=query.yell_datetime,
    )
    # except:
    #     return '404'   # }}}


def send_temp_dict(ws, temp_dict):
    temp_dict = dict(
        sorted(
            temp_dict.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    print(temp_dict)
    for result in temp_dict:
        ws.send(result)


@sock.route('/yell/search/<searched>')  # {{{
def get_yell_multi(ws, searched):
    # if session.get('ws'):
    #     ws = session['ws']
    # else:
    #     session['ws'] = ws
    # print('socketd', ws, searched)

    all = db.session.execute(db.select(Post)).scalars().all()
    threshold = 80
    temp_dict = {}
    # print('not waiting')
    for idx, query in enumerate(all, 1):
        # print(idx)
        if len(temp_dict) >= 15:

            send_temp_dict(ws, temp_dict)
            temp_dict = {}
            while True:
                data = ws.receive()
                if data == 'next':
                    # print('recieved')
                    break

        temp_dict[query.yell_id] = 0
        eval = [
            query.yell_datetime,
            query.yell_description,
            query.yell_code,
            query.yell_filename,
            query.yell_title,
        ]
        for idx, item in enumerate(eval):
            ratio = fuzz.ratio(str(searched), str(item))
            temp_dict[query.yell_id] += ratio * idx
        temp_dict[query.yell_id] /= 5
        print(temp_dict)
        if temp_dict[query.yell_id] < threshold:
            temp_dict.pop(query.yell_id)
    send_temp_dict(ws, temp_dict)
    ws.send('404')


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
            Post(
                yell_id=i,
                yell_maker_id=fake_user,
                yell_title=randomword(50),
                yell_description=randomword(500),
                yell_code=randomword(1000),
                yell_filename=randomword(15),
            )
        )

    db.session.commit()


# }}}

if __name__ == '__main__':
    with app.app_context():
        insert_random(db, 10000)
    app.run(host='localhost')
