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
from datetime import datetime
from markdown import extensions, markdown
from markdown.extensions.fenced_code import FencedCodeExtension as fenced_code
from markdown.extensions.codehilite import CodeHiliteExtension as codehilite
from rapidfuzz import fuzz
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

# Flask-SQLAlchemy Database{{{
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
        db.DateTime, nullable=False, default=datetime.utcnow().isoformat
    )

    def __repr__(self):
        return f'<Yell {self.yell_id} {self.yell_title}>'


class Pst(db.Model):
    post_content_id = db.Column(db.Integer, primary_key=True, nullable=False)
    original_yell_id = db.Column(
        db.Integer, db.ForeignKey('yell.yell_id'), nullable=False
    )
    post_description = db.Column(db.String(1000), nullable=False)
    post_code = db.Column(db.Text, nullable=False)
    post_filename = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Pst id: {self.post_content_id} original: {self.original_yell_id}>'


class Req(db.Model):
    request_content_id = db.Column(
        db.Integer, primary_key=True, nullable=False
    )
    original_yell_id = db.Column(
        db.Integer, db.ForeignKey('yell.yell_id'), nullable=False
    )
    request_content = db.Column(db.Text, nullable=False)


class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    original_yell_id = db.Column(
        db.Integer, db.ForeignKey('yell.yell_id'), nullable=False
    )
    tag_content = db.Column(db.String, nullable=False)
    tag_type = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Tag {self.tag_id} {self.tag_content}>'


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    original_yell_id = db.Column(
        db.Integer, db.ForeignKey('yell.yell_id'), nullable=False
    )
    comment_content = db.Column(db.String, nullable=False)
    comment_datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    )

    def __repr__(self):
        return f'<Comment {self.comment_id} {self.comment_content}>'


with app.app_context():
    db.create_all()
# }}}


# Other{{{
@login_manager.user_loader
def load_user(id):
    # return User.query.get(id)
    return db.session.get(User, id)


@app.errorhandler(404)
def page_not_found(error):
    return redirect('/')


# }}}


@app.route('/')  # {{{
def index():
    # print(current_user.is_authenticated)
    # print(current_user.is_active)
    # print(current_user.is_anonymous)
    return render_template('index.html', current_user=current_user)


# }}}


@app.route('/register', methods=['GET', 'POST'])  # {{{
def register():
    if request.method == 'POST':
        send_error = lambda warning: render_template(
            'register.html',
            warning=warning,
            username=username or '',
            password=password or '',
            confirm_password=confirm_password or '',
        )

        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not username:
            return send_error('Must provide a username')
        elif not password:
            return send_error('Must provide a password')
        elif not confirm_password:
            return send_error('Must provide a confirmation password')
        elif not username or not password or not confirm_password:
            return send_error('Do not leave the input blank')
        elif password != confirm_password:
            return send_error('Passwords are not the same')
        elif len(username) < 4 or len(password) < 4:
            return send_error(
                'Username or password must be atleast 4 characters long'
            )
        elif len(username) > 50 or len(password) > 50:
            return send_error(
                'Username or password must not be longer than 50 characters'
            )
        elif not username.isalnum():
            return send_error(
                'Usernames must only contain English characters or numbers'
            )
        elif ' ' in password and password.isascii():
            return send_error(
                'Usernames must only contain English characters or numbers'
            )

        username = username.lower()
        check = db.session.execute(
            db.select(User).filter_by(username=username)
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
    elif current_user.is_anonymous:
        return render_template('register.html')
    else:
        return redirect(url_for('index'))  # }}}


@app.route('/login', methods=['GET', 'POST'])  # {{{
@login_manager.unauthorized_handler
def login():
    if request.method == 'POST':
        send_error = lambda warning: render_template(
            'login.html',
            warning=warning,
            username=username or '',
            password=password or '',
        )
        username = request.form.get('username')
        password = request.form.get('password')
        if not username:
            return send_error('Must provide a username')
        elif not password:
            return send_error('Must provide a password')
        username = username.lower()
        query = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar()

        if not query:
            return send_error('That user does not exist')
        hash = query.hash
        if not bcrypt.check_password_hash(hash, password):
            return send_error('Wrong password')

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
        send_error = lambda warning: render_template(
            'post.html',
            warning=warning,
            current_user=current_user,
            title=title or '',
            description=description or '',
            filename=filename or '',
            code=code or '',
        )
        user_id = current_user.get_id()
        title = request.form.get('title')
        description = request.form.get('description')
        filename = request.form.get('filename')
        code = request.form.get('code')
        if not user_id:
            return redirect(url_for('register'))
        elif not title:
            return send_error('Must provide a title')
        elif not description:
            return send_error('Must provide a description')
        elif not filename:
            return send_error('Must have a file name')
        elif not code:
            return send_error('Must provide code')
        elif ' ' in filename:
            return send_error(
                'There should not be any whitespace in filenames',
            )
        elif not len(title) >= 3 or not len(title) <= 100:
            return send_error(
                'Titles must be atleast 3 characters long and a maximum of 100',
            )
        elif not len(description) >= 3 or not len(description) <= 1000:
            return send_error(
                'Description must be atleast 3 characters long and a maximum of 1000',
            )
        elif not len(filename) >= 3 or not len(filename) <= 50:
            return send_error(
                'Filenames must be atleast 3 characters long and a maximum of 50',
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
        filename = clean_text(filename)

        try:
            lexer = guess_lexer_for_filename(filename, code)
            code = highlight(
                code,
                lexer,
                HtmlFormatter(
                    style='one-dark',
                    linenos='table',
                    wrapcode=True,
                ),
            )
        except:
            code = clean_text(code)

        yell = Yell(
            author_id=user_id,
            yell_title=title,
            yell_type='pst',
        )
        db.session.add(yell)
        db.session.flush()
        db.session.add(
            Pst(
                original_yell_id=yell.yell_id,
                post_description=description,
                post_code=code,
                post_filename=filename,
            )
        )
        db.session.commit()

        return redirect(url_for('index'))
    else:
        return render_template(
            'post.html',
            current_user=current_user,
        )


# }}}


@app.route('/create/request', methods=['GET', 'POST'])  # {{{
@login_required
def post_request():
    if request.method == 'POST':
        return render_template('post_request.html')
    else:
        return render_template(
            'request.html',
            current_user=current_user,
        )


# }}}


@app.route('/yell/<yell_id>')  # {{{
def get_yell(yell_id):
    if yell_id == 'last':
        query = db.session.execute(
            db.select(Yell).order_by(Yell.yell_id.desc())
        ).scalar()
    elif yell_id == 'rated':
        query = db.session.execute(
            db.select(Yell).order_by(Yell.yell_rating.desc())
        ).scalar()
    else:
        query = db.session.get(Yell, yell_id)
        db.session.get
    if not query:
        return '404'

    match (query.yell_type):
        case 'pst':
            post = db.session.execute(
                db.select(Pst).filter_by(original_yell_id=query.yell_id)
            ).scalar()
            return jsonify(
                yell_id=query.yell_id,
                author=db.session.get(User, query.author_id).username,
                yell_title=query.yell_title,
                yell_rating=query.yell_rating,
                yell_type=query.yell_type,
                yell_datetime=query.yell_datetime,
                post_code=post.post_code,
                post_description=post.post_description,
                post_filename=post.post_filename,
            )

        case 'req':
            return 'balls'

        case _:
            return '404'
    # except:
    #     return '404'   # }}}


@sock.route('/yell/search/<searched>')  # {{{
def get_yell_multi(ws, searched):
    all = db.session.execute(db.select(Yell)).scalars().all()
    threshold = 80
    temp_dict = {}
    for idx, query in enumerate(all, 1):
        if len(temp_dict) >= 15:

            send_temp_dict(ws, temp_dict)
            temp_dict = {}
            while True:
                data = ws.receive()
                if data == 'next':
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
        if temp_dict[query.yell_id] < threshold:
            temp_dict.pop(query.yell_id)
    send_temp_dict(ws, temp_dict)
    ws.send('404')


def send_temp_dict(ws, temp_dict):
    temp_dict = dict(
        sorted(
            temp_dict.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    for result in temp_dict:
        ws.send(result)


# }}}


# def insert_random(db, max):  # {{{
#     import random, string
#
#     def randomword(length):
#         letters = string.ascii_lowercase
#         return ''.join(random.choice(letters) for i in range(length))
#
#     for i in range(max):
#         # print(i)
#
#         fake_user = i
#         # fake_user = random.randint(0, max)
#         db.session.add(
#             User(
#                 id=fake_user,
#                 username=randomword(50),
#                 # hash=bcrypt.generate_password_hash(randomword(50)),
#                 hash=randomword(50),
#             )
#         )
#         db.session.add(
#             Yell(
#                 yell_id=i,
#                 yell_author_id=fake_user,
#                 yell_title=randomword(50),
#                 yell_description=randomword(500),
#                 yell_code=randomword(1000),
#                 yell_filename=randomword(15),
#             )
#         )
#
#     db.session.commit()
#
#
# with app.app_context():
#     insert_random(db, 10000)
#
#
# # }}}

if __name__ == '__main__':
    app.run(host='localhost')
