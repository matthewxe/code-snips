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
from markdown import markdown
from markdown.extensions.fenced_code import FencedCodeExtension as fenced_code
from markdown.extensions.codehilite import CodeHiliteExtension as codehilite
from rapidfuzz import fuzz, utils
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    inspect,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List

# Print decorators
LOG = '\033[100;92mLOG ::'
END = '\033[0m'
# Flask Setup {{{
app = Flask(__name__)
sock = Sock(app)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 7}
import os

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SECURITY_PASSWORD_SALT'] = os.environ['SECURITY_PASSWORD_SALT']
# Bcrypt Setup
bcrypt = Bcrypt(app)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
# }}}
# Flask-SQLAlchemy Database{{{

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = 'user_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    hash: Mapped[str] = mapped_column(String(60), nullable=False)

    def __repr__(self):
        return f'<User {self.id} {self.username}>'


class Yell(db.Model):
    __tablename__ = 'yell_table'
    yell_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey('user_table.id'), nullable=False
    )
    author: Mapped['User'] = relationship()
    yell_title: Mapped[str] = mapped_column(String(100), nullable=False)
    yell_type: Mapped[str] = mapped_column(String(3), nullable=False)
    yell_datetime: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow()
    )

    yell_rating: Mapped[int] = mapped_column(Integer, default=0)
    yell_comments: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self):
        return f'<Yell id: {self.yell_id} author: {self.author} title: {self.yell_title}>'


class Post(db.Model):
    base_yell_id = mapped_column(
        ForeignKey('yell_table.yell_id'), nullable=False
    )
    base_yell: Mapped['Yell'] = relationship()
    post_content_id: Mapped[int] = mapped_column(primary_key=True)
    post_description: Mapped[str] = mapped_column(String(5000), nullable=False)
    post_code: Mapped[Text] = mapped_column(Text, nullable=False)
    post_filename: Mapped[str] = mapped_column(String(50), nullable=False)

    def __repr__(self):
        return (
            f'<Post id: {self.post_content_id} filename: {self.post_filename}>'
        )


class Request(db.Model):
    base_yell_id: Mapped[int] = mapped_column(
        ForeignKey('yell_table.yell_id'), nullable=False
    )
    base_yell: Mapped['Yell'] = relationship()
    request_content_id: Mapped[int] = mapped_column(primary_key=True)
    request_content: Mapped[str] = mapped_column(Text, nullable=False)
    request_state: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f'<Request id: {self.request_content_id} content: {self.request_content}>'


class CommentSet(db.Model):
    __tablename__ = 'comment_set_table'
    original_yell_id: Mapped[int] = mapped_column(
        ForeignKey('yell_table.yell_id')
    )
    comment_set_id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[List['Comment']] = relationship()


class Comment(db.Model):
    __tablename__ = 'comment_table'
    comment_id: Mapped[int] = mapped_column(primary_key=True)
    comment_set_id: Mapped[int] = mapped_column(
        ForeignKey('comment_set_table.comment_set_id'), nullable=False
    )
    base_yell_id: Mapped[int] = mapped_column(
        ForeignKey('yell_table.yell_id'), nullable=False
    )
    base_yell: Mapped['Yell'] = relationship()
    comment_content: Mapped[str] = mapped_column(String(5000), nullable=False)

    # thanks rubber duck
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Comment id: {self.comment_id} author: {self.base_yell.author} content: {self.comment_content}>'


class Tag(db.Model):
    tag_id: Mapped[int] = mapped_column(primary_key=True)
    original_yell_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('yell_table.yell_id'), nullable=False
    )
    tag_content: Mapped[str] = mapped_column(db.String(180), nullable=False)

    def __repr__(self):
        return f'<Tag id: {self.tag_id} original: {self.original_yell_id} content: {self.tag_content}>'


class Rating(db.Model):
    rating_id: Mapped[int] = mapped_column(primary_key=True)
    original_yell_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('yell_table.yell_id'), nullable=False
    )
    rating: Mapped[bool] = mapped_column(Boolean)
    critic_id: Mapped[int] = mapped_column(
        ForeignKey('user_table.id'), nullable=False
    )
    # author: Mapped['User'] = relationship()

    def __repr__(self):
        return f'<Rating id: {self.rating_id} critic: {self.critic_id} rate: {self.rating}>'

class Report(db.Model):
    report_id: Mapped[int] = mapped_column(primary_key=True)
    original_yell_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('yell_table.yell_id'), nullable=False
    )
    report: Mapped[str] = mapped_column(String(5000), nullable=False)
    reporter_id: Mapped[int] = mapped_column(
        ForeignKey('user_table.id'), nullable=False
    )


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
            return send_error('That user already exists')

        hash = bcrypt.generate_password_hash(password)

        db.session.add(User(username=username, hash=hash))
        db.session.commit()

        # elif current_user.is_anonymous:
        #     return render_template('register.html')
        prev = request.form.get('prev')
        if prev:
            return redirect('/login?prev=' + prev)
        else:
            return redirect(url_for('login'))
    else:
        return render_template('register.html', prev=request.args.get('prev'))


# }}}
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
        prev = request.form.get('prev')
        if prev:
            return redirect(prev)
        else:
            return redirect(url_for('index'))
    else:
        return render_template(
            'login.html',
            warning=request.args.get('warning'),
            prev=request.args.get('prev'),
        )


# }}}
@app.route('/logout')  # {{{
def logout():
    logout_user()
    prev = request.args.get('prev')
    if prev:
        return redirect(prev)
    else:
        return redirect(url_for('index'))


# }}}
@app.route('/discover')  # {{{
def discover():
    return render_template(
        'discover.html', current_user=current_user, type='post'
    )


# }}}
@app.route('/requests')  # {{{
def requests():
    return render_template(
        'discover.html', current_user=current_user, type='request'
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
            tags=tags or '',
            filename=filename or '',
            code=code or '',
        )
        user_id = current_user.get_id()
        title = request.form.get('title')
        description = request.form.get('description')
        tags = request.form.get('tags')
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

        clean_title = clean_text(title)
        clean_filename = clean_text(filename)

        clean_description = markdown(
            clean(description),
            extensions=[
                codehilite(css_class='highlight', pygments_style='one-dark'),
                fenced_code(),
            ],
        )

        try:
            lexer = guess_lexer_for_filename(filename, code)
            clean_code = highlight(
                code,
                lexer,
                HtmlFormatter(
                    cssclass='highlight',
                    style='one-dark',
                    linenos='table',
                    wrapcode=True,
                ),
            )
        except:
            clean_code = clean_text(code)

        yell = Yell(
            author_id=user_id,
            yell_title=clean_title,
            yell_type='pst',
        )
        db.session.add(yell)
        db.session.flush()

        if tags:
            cleaned_tags = {tag.strip() for tag in tags.split(',')}
            if len(cleaned_tags) > 10:
                return send_error(
                    'Tags should not go above 10',
                )
            cleaned_cleaned_tags = []
            for tag in cleaned_tags:
                if len(tag) > 30:
                    return send_error(
                        'A tag must not be longer than 30 characters'
                    )
                cleaned_cleaned_tags.append(clean_text(tag))

            for tag in cleaned_tags:
                tag_db = Tag(
                    original_yell_id=yell.yell_id,
                    tag_content=tag,
                )
                db.session.add(tag_db)
                db.session.flush()

        db.session.add(
            Post(
                base_yell_id=yell.yell_id,
                post_description=clean_description,
                post_code=clean_code,
                post_filename=clean_filename,
            )
        )

        db.session.add(
            CommentSet(
                original_yell_id=yell.yell_id,
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
def req():
    if request.method == 'POST':
        send_error = lambda warning: render_template(
            'request.html',
            warning=warning,
            current_user=current_user,
            title=title or '',
            # filename=filename or '',
            tags=tags or '',
            content=content or '',
        )
        user_id = current_user.get_id()
        title = request.form.get('title')
        tags = request.form.get('tags')
        # filename = request.form.get('filename')
        content = request.form.get('content')
        if not user_id:
            return redirect(url_for('register'))
        # elif not filename:
        #     return send_error('Must have a file name')
        elif not title:
            return send_error('Must provide a title')
        elif not content:
            return send_error('Must provide a body')
        elif not len(title) >= 3 or not len(title) <= 100:
            return send_error(
                'Titles must be atleast 3 characters long and a maximum of 100',
            )
        elif not len(content) >= 3 or not len(content) <= 1000:
            return send_error(
                'Description must be atleast 3 characters long and a maximum of 1000',
            )

        clean_title = clean_text(title)
        clean_content = markdown(
            clean(content),
            extensions=[
                codehilite(css_class='highlight', pygments_style='one-dark'),
                fenced_code(),
            ],
        )

        yell = Yell(
            author_id=user_id,
            yell_title=clean_title,
            yell_type='req',
        )
        db.session.add(yell)
        db.session.flush()

        if tags:
            cleaned_tags = {tag.strip() for tag in tags.split(',')}
            if len(cleaned_tags) > 10:
                return send_error(
                    'Tags should not go above 10',
                )
            cleaned_cleaned_tags = []
            for tag in cleaned_tags:
                if len(tag) > 30:
                    return send_error(
                        'A tag must not be longer than 30 characters'
                    )
                cleaned_cleaned_tags.append(clean_text(tag))

            for tag in cleaned_tags:
                tag_db = Tag(
                    original_yell_id=yell.yell_id,
                    tag_content=tag,
                )
                db.session.add(tag_db)
                db.session.flush()

        db.session.add(
            Request(
                base_yell_id=yell.yell_id,
                request_content=clean_content,
            )
        )
        db.session.add(
            CommentSet(
                original_yell_id=yell.yell_id,
            )
        )
        db.session.commit()

        return redirect(url_for('index'))
    else:
        return render_template(
            'request.html',
            current_user=current_user,
        )


# }}}
# /<any(post, request, comment):yell_type>/<id>  {{{
# Thanks cs50.ai for the route tricks
@app.route(
    '/<any(post, request, comment):yell_type>/<id>', methods=['GET', 'POST']
)
def yell_page(yell_type, id):
    if request.method == 'POST':
        send_error = lambda warning: render_template(
            'yell.html',
            warning=warning,
            yell_type=yell_type,
            id=id,
            current_user=current_user,
            comment=comment,
        )
        user_id = current_user.get_id()
        if not user_id:
            return send_error('You must be logged in')
        comment = request.form.get('comment_content')
        if not comment:
            return send_error('Cannot send blank comment')
        elif not len(comment) >= 3 or not len(comment) <= 1000:
            return send_error(
                'Comments must be atleast 3 characters long and a maximum of 1000',
            )
        comment = markdown(
            clean(comment),
            extensions=[
                codehilite(css_class='highlight', pygments_style='one-dark'),
                fenced_code(),
            ],
        )

        match (yell_type):
            case 'post':
                data = db.session.get(Post, id)
            case 'request':
                data = db.session.get(Request, id)
            case 'comment':
                data = db.session.get(Comment, id)
            case _:
                return send_error(
                    'Something went wrong, please report this error, CODE: 1'
                )

        if not data:
            return send_error(
                'Something went wrong, please report this error, CODE: 3'
            )

        db.session.execute(
            db.update(Yell)
            .filter_by(yell_id=data.base_yell_id)
            .values(yell_comments=data.base_yell.yell_comments + 1)
        )
        commentset = db.session.execute(
            db.select(CommentSet).filter_by(original_yell_id=data.base_yell_id)
        ).scalar()
        if not commentset:
            return send_error(
                'Something went wrong, please report this error, CODE:2'
            )

        yell = Yell(
            author_id=user_id,
            yell_title='',
            yell_type='com',
        )
        db.session.add(yell)
        db.session.flush()

        db.session.add(
            CommentSet(
                original_yell_id=yell.yell_id,
            )
        )
        db.session.add(
            Comment(
                base_yell_id=yell.yell_id,
                comment_set_id=commentset.comment_set_id,
                comment_content=comment,
            )
        )

        db.session.commit()
        return redirect(request.url)

    else:
        return render_template(
            'yell.html', yell_type=yell_type, id=id, current_user=current_user
        )


# }}}
# /<any(post, request, comment):yell_type>/<id>/<rate_type>  {{{
@app.route(
    '/<any(post, request, comment):yell_type>/<id>/<any(like, unlike):rate_type>',
    
)
def do_rate(yell_type, id, rate_type):
    critic_id = current_user.get_id()
    if not critic_id:
        return 'unlogged'

    match (yell_type):
        case 'post':
            data = db.session.get(Post, id)
        case 'request':
            data = db.session.get(Request, id)
        case 'comment':
            data = db.session.get(Comment, id)
        case _:
            return '404'
    original_yell_id = data.base_yell_id


    if rate_type == 'status':
        rating = db.session.execute(
            db.select(Rating).filter_by(
                original_yell_id=original_yell_id
            )
        ).scalar()
        return str(rating.rating)


    rating = db.session.execute(
        db.select(Rating).filter_by(
            original_yell_id=original_yell_id, critic_id=int(critic_id)
        )
    ).scalar()
    if not rating:
        if rate_type == 'unlike':
            return 'false_unlike'
        elif rate_type == 'status':
            return 'False'
        rate_type == 'like'
        new_rating = Rating(
            original_yell_id=original_yell_id,
            rating=True,
            critic_id=(critic_id),
        )
        db.session.add(new_rating)
        db.session.execute(
            db.update(Yell)
            .filter_by(yell_id=original_yell_id)
            .values(yell_rating=Yell.yell_rating + 1)
        )
    else:
        if rate_type == 'unlike':
            match (rating.rating):
                case False:
                    return 'already_unliked'
                case True:
                    db.session.execute(
                        db.update(Rating)
                        .filter_by(
                            original_yell_id=original_yell_id,
                            critic_id=int(critic_id),
                        )
                        .values(rating=False)
                    )
                    db.session.execute(
                        db.update(Yell)
                        .filter_by(yell_id=original_yell_id)
                        .values(yell_rating=Yell.yell_rating - 1)
                    )
        elif rate_type == 'like':
            match (rating.rating):
                case True:
                    return 'already_liked'
                case False:
                    db.session.execute(
                        db.update(Rating)
                        .filter_by(
                            original_yell_id=original_yell_id,
                            critic_id=int(critic_id),
                        )
                        .values(rating=True)
                    )
                    db.session.execute(
                        db.update(Yell)
                        .filter_by(yell_id=original_yell_id)
                        .values(yell_rating=Yell.yell_rating + 1)
                    )
    db.session.commit()
    return 'yay'


# }}}
# /<any(post, request, comment):yell_type>/<id>/status  {{{
@app.route('/<any(post, request, comment):yell_type>/<id>/status')
def rate_status(yell_type, id):
    critic_id = current_user.get_id()
    if not critic_id:
        return 'False'

    match (yell_type):
        case 'post':
            data = db.session.get(Post, id)
        case 'request':
            data = db.session.get(Request, id)
        case 'comment':
            data = db.session.get(Comment, id)
        case _:
            return '404'

    if not data:
        return 'False'

    original_yell_id = data.base_yell_id
    rating = db.session.execute(
        db.select(Rating).filter_by(
            original_yell_id=original_yell_id, critic_id=int(critic_id)
        )
    ).scalar()
    if not rating:
        return 'False'
    return str(rating.rating)


# }}}
# /<any(post, request, comment):yell_type>/<id>/report  {{{
@app.route(
    '/<any(post, request, comment):yell_type>/<id>/report',
    methods=['GET', 'POST'],
)
def report_yell(yell_type, id):
    if request.method == 'POST':
        send_error = lambda warning: render_template(
            'post.html',
            warning=warning,
            current_user=current_user,
            report=report or '',
        )
        user_id = current_user.get_id()
        report = request.form.get('report')
        if not user_id or current_user.is_authenticated != True:
            return redirect(url_for(f'login?prev=/{yell_type}/{id}/report'))
        elif not report:
            return send_error('Must provide a report')
        elif not len(report) >= 3 or not len(report) <= 1000:
            return send_error(
                'report must be atleast 3 characters long and a maximum of 1000',
            )


        match (yell_type):
            case 'post':
                data = db.session.get(Post, id)
            case 'request':
                data = db.session.get(Request, id)
            case 'comment':
                data = db.session.get(Comment, id)
            case _:
                return send_error(
                    'Something went wrong, please report this error, CODE: 1'
                )
        if not data:
            return send_error(
                'Something went wrong, please report this error, CODE: 4',
            )
        original_yell_id = data.original_yell_id

        reported = Report(original_yell_id=original_yell_id,report=report,reporter_id=user_id)
        db.session.add(reported)
        db.session.commit()
            
        return redirect(f"/{yell_type}/{id}")
    else:
        user_id = current_user.get_id()
        if not user_id or current_user.is_authenticated == False:
            return redirect(f"/login?prev=/{yell_type}/{id}/report")
        return render_template('report.html', current_user=current_user)


# }}}
# # /<any(post, request, comment):yell_type>/<id>/delete  {{{
# @app.route(
#     '/<any(post, request, comment):yell_type>/<id>/delete',
#     methods=['GET', 'POST'],
# )
# def delete_yell(yell_type, id, report):
#     return 'yay'
#
#
# # }}}
# # /<any(post, request, comment):yell_type>/<id>/edit  {{{
# @app.route(
#     '/<any(post, request, comment):yell_type>/<id>/edit',
#     methods=['GET', 'POST'],
# )
# def edit_yell(yell_type, id):
#     match (yell_type):
#         case 'post':
#             data = db.session.get(Post, id)
#         case 'request':
#             data = db.session.get(Request, id)
#         case 'comment':
#             data = db.session.get(Comment, id)
#         case _:
#             return send_error(
#                 'Something went wrong, please report this error, CODE: 1'
#             )
#
#     if not data:
#         return send_error(
#             'Something went wrong, please report this error, CODE: 3'
#         )
#     return 'yay'
#
#
# # }}}
@app.route('/request/<id>/mark')   # {{{
def mark_yell(id):
    critic_id = current_user.get_id()
    if not critic_id:
        return 'not logged in'
    data = db.session.get(Request, id)
    if not data:
        return 'request does not exist'

    if not critic_id == data.base_yell.author_id:
        return 'failed'


    print(data.request_state)
    print(not data.request_state)
    shit = not data.request_state
    db.session.execute(
        db.update(Request)
        .filter_by(request_content_id=data.request_content_id)
        .values(request_state=shit)
    )
    db.session.commit()

    return redirect('/request/' + id)


# }}}
@app.route('/api/yell/<yell_id>')  # {{{
def get_yell(yell_id):
    if yell_id == 'last':
        base = db.session.execute(
            db.select(Yell).order_by(Yell.yell_id.desc())
        ).scalar()
    elif yell_id == 'rated':
        base = db.session.execute(
            db.select(Yell).order_by(Yell.yell_rating.desc())
        ).scalar()
    else:
        base = db.session.get(Yell, yell_id)

    if not base:
        return '404'

    match (base.yell_type):
        case 'pst':
            return get_post(base.yell_id)
        case 'req':
            return get_request(base.yell_id)
        case 'com':
            return get_comment(base.yell_id)
        case _:
            return '404'


# }}}
@app.route('/api/post/<post_id>')  # {{{
@app.route('/api/pst/<post_id>')
# @login_required
def get_post(post_id):
    if post_id == 'last':
        post = db.session.execute(
            db.select(Post).order_by(Post.post_content_id.desc())
        ).scalar()
    elif post_id == 'rated':
        post = db.session.execute(
            db.select(Post).order_by(Post.base_yell.rating.desc())
        ).scalar()
    else:
        post = db.session.get(Post, post_id)
        if not post:
            post = db.session.execute(
                db.select(Post).filter_by(base_yell_id=post_id)
            ).scalar()
    if not post:
        return '404'

    base = post.base_yell
    if current_user.is_authenticated == False:
        owned = False
    else:
        owned = base.author.id == int(current_user.get_id())

    return jsonify(
        base_id=base.yell_id,
        base_title=base.yell_title,
        base_rating=base.yell_rating,
        base_comments=base.yell_comments,
        base_datetime=base.yell_datetime.isoformat(),
        base_type=base.yell_type,
        author=base.author.username,
        owned=owned,
        content_id=post.post_content_id,
        post_code=post.post_code,
        post_description=post.post_description,
        post_filename=post.post_filename,
    )


# }}}
@app.route('/api/request/<request_id>')  # {{{
@app.route('/api/req/<request_id>')
# @login_required
def get_request(request_id):
    if request_id == 'last':
        req = db.session.execute(
            db.select(Request).order_by(Request.request_content_id.desc())
        ).scalar()

        print(LOG, 'if get_request', req, END)
    elif request_id == 'rated':
        req = db.session.execute(
            db.select(Request).order_by(Request.base_yell.rating.desc())
        ).scalar()
        print(LOG, 'elif get_request', req, END)
    else:
        req = db.session.get(Request, request_id)
        if not req:
            req = db.session.execute(
                db.select(Request).filter_by(base_yell_id=request_id)
            ).scalar()

    if not req:
        return '404'

    base = req.base_yell

    if current_user.is_authenticated == False:
        owned = False
    else:
        owned = base.author.id == int(current_user.get_id())
    return jsonify(
        base_id=base.yell_id,
        base_title=base.yell_title,
        base_rating=base.yell_rating,
        base_comments=base.yell_comments,
        base_datetime=base.yell_datetime.isoformat(),
        base_type=base.yell_type,
        author=base.author.username,
        owned=owned,
        content_id=req.request_content_id,
        request_content=req.request_content,
        request_state=req.request_state,
    )


# }}}
@app.route('/api/commentset/<yell_id>')  # {{{
# @login_required
def get_commentset(yell_id):
    commentset = db.session.execute(
        db.select(CommentSet).filter_by(original_yell_id=yell_id)
    ).scalar()
    if not commentset:
        return '404'

    comments = [c.to_dict() for c in commentset.comment]

    return jsonify(
        original_yell_id=commentset.original_yell_id,
        comment_set_id=commentset.comment_set_id,
        comments=comments,
    )


# }}}
@app.route('/api/comment/<comment_id>')  # {{{
# @login_required
def get_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    if not comment:
        comment = db.session.execute(
            db.select(Comment).filter_by(base_yell_id=comment_id)
        ).scalar()
        if not comment:
            return '404'

    base = comment.base_yell

    if current_user.is_authenticated == False:
        owned = False
    else:
        owned = base.author.id == int(current_user.get_id())
    return jsonify(
        base_id=base.yell_id,
        base_title=base.yell_title,
        base_rating=base.yell_rating,
        base_comments=base.yell_comments,
        base_datetime=base.yell_datetime.isoformat(),
        base_type=base.yell_type,
        author=base.author.username,
        owned=owned,
        content_id=comment.comment_id,
        comment_set_id=comment.comment_set_id,
        comment_content=comment.comment_content,
    )


# }}}
@app.route('/api/tags/<yell_id>')  # {{{
# @login_required
def get_tags(yell_id):
    tags = (
        db.session.execute(db.select(Tag).filter_by(original_yell_id=yell_id))
        .scalars()
        .all()
    )
    if not tags:
        return '404'
    tags = [tag.tag_content for tag in tags]
    return jsonify(tags)


# }}}
@sock.route('/api/yell/search/<searched>')  # {{{
# @login_required
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

        match (query.yell_type):
            case 'pst':
                post = db.session.execute(
                    db.select(Post).filter_by(base_yell_id=query.yell_id)
                ).scalar()
                if not post:
                    return '404'
                eval = [
                    post.post_description,
                    post.post_code,
                    post.post_filename,
                    query.author.username,
                    query.yell_datetime,
                    query.yell_rating,
                    query.yell_title,
                ]
            case 'req':
                req = db.session.execute(
                    db.select(Request).filter_by(base_yell_id=query.yell_id)
                ).scalar()
                if not req:
                    return '404'
                eval = [
                    req.request_content,
                    query.author.username,
                    query.yell_datetime,
                    query.yell_rating,
                    query.yell_title,
                ]
            case 'com':
                # TODO: maybe implement
                continue
            case _:
                continue

        for idx, item in enumerate(eval):
            ratio = fuzz.WRatio(
                str(searched), str(item), processor=utils.default_process
            )
            temp_dict[query.yell_id] += ratio * idx
        temp_dict[query.yell_id] /= len(eval)
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


if __name__ == '__main__':
    app.run(host='localhost')
