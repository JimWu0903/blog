from flask import Flask, render_template, redirect, url_for, jsonify, request, flash, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

# since gravatar api broken, this is alternative ways
from hashlib import sha256
from urllib.parse import urlencode

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

from forms import PostForm, RegisterForm, LoginForm, CommentForm
import os

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_KEY")
Bootstrap5(app)
ckeditor = CKEditor(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


# 如果找到了 "DB_URL" 環境變量，它會返回該變量的值。
# 如果沒有找到 "DB_URL" 環境變量，它會返回默認值 'sqlite:///blogs.db'。
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL", 'sqlite:///blogs.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Set flask_login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
        return user
    except Exception as e:
        return abort(403)
    # return db.get_or_404(User, user_id)


def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            pass
        else:
            return abort(403)

        return f(*args, **kwargs)

    return wrapper


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[int] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    posts: Mapped[list["BlogPost"]] = db.relationship("BlogPost", back_populates="author")
    comments: Mapped[list["Comment"]] = db.relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = db.relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    # ***************Parent Relationship*************#
    comments = db.relationship("Comment", back_populates="parent_post")

    @property
    def author_name(self):
        return self.author.name if self.author else "Unknown"

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<BlogPost {self.title},{self.date}>'


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = db.relationship("User", back_populates="comments")

    # ***************Child Relationship*************#
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = db.relationship("BlogPost", back_populates="comments")
    text: Mapped[str] = mapped_column(Text, nullable=False)


def add_user(form):
    hash_pw = generate_password_hash(
        form.password.data,
        method="pbkdf2:sha256",
        salt_length=8)
    try:
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_pw
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
    except Exception as e:
        db.session.rollback()
        return jsonify(error={"failure Something went wrong": str(e)}), 500


def get_current_date():
    # 獲取當前日期和時間
    current_date = datetime.now()

    # 格式化日期
    formatted_date = current_date.strftime("%B %d, %Y")
    return formatted_date


def add_post(form):
    try:
        new_blog_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=get_current_date(),
            author=current_user,
            img_url=form.img_url.data,
            body=form.body.data
        )
        db.session.add(new_blog_post)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(error={"failure Something went wrong": str(e)}), 500


def update_post(form, post_to_edit):
    try:
        post_to_edit.title = form.title.data
        post_to_edit.subtitle = form.subtitle.data
        post_to_edit.title = form.title.data
        post_to_edit.date = get_current_date()
        post_to_edit.author = form.author.data
        post_to_edit.img_url = form.img_url.data
        post_to_edit.body = form.body.data

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(error={"failure Something went wrong": str(e)}), 500


# since gravatar api broken, this is alternative ways
def gravatar_url(email, size=100, rating='g', default='retro', force_default=False, ):
    hash_value = sha256(email.lower().encode('utf-8')).hexdigest()
    query_params = urlencode({'d': default, 's': str(size), 'r': rating, 'f': force_default})
    return f"https://www.gravatar.com/avatar/{hash_value}?{query_params}"


# since gravatar api broken, this is alternative ways
app.jinja_env.filters['gravatar'] = gravatar_url


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    if current_user.is_authenticated:
        if current_user.id == 1:
            return render_template("index.html", all_posts=posts, admin=True)
    return render_template("index.html", all_posts=posts, admin=False)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    email = form.email.data
    user = User.query.filter_by(email=email).first()
    if form.validate_on_submit() and not user:
        add_user(form)
        return redirect(url_for('get_all_posts', logged_in=True))
    elif form.validate_on_submit():
        flash('The Email address already register!')
    return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('get_all_posts', logged_in=True))
        else:
            flash('Email or Password mismatch.')
            return redirect(url_for('login'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts', logged_in=False))


# TODO: Add a route so that you can click on individual posts.
@app.route('/show_post/<int:post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    comments = requested_post.comments
    comment_form = CommentForm()
    return render_template("post.html",
                           post=requested_post,
                           form=comment_form,
                           comments=comments)


@app.route('/add-comment', methods=["POST"])
def add_comment():
    if not current_user.is_authenticated:
        flash("You need to login to leave comment on the post")
        return redirect(url_for('login'))

    author_id = current_user.id
    post_id = request.form.get('post_id')
    comment_text = request.form.get('comment')
    try:
        new_comment = Comment(
            author_id=author_id,
            post_id=post_id,
            text=comment_text,
        )
        db.session.add(new_comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(error={"failure Something went wrong": str(e)}), 500
    return redirect(url_for('show_post', post_id=post_id))


# TODO: add_new_post() to create a new blog post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        add_post(form)
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form, is_edit=False)


# TODO: edit_post() to change an existing blog post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post_to_edit = db.get_or_404(BlogPost, post_id)
    # since PostForm & BlogPost fields pretty much the same
    form = PostForm(obj=post_to_edit)
    # 編輯模式改變按鈕外顯文字
    form.submit.label.text = "Update Post"
    if form.validate_on_submit():
        update_post(form, post_to_edit)
        return redirect(url_for('show_post', post_id=post_id))
    return render_template("make-post.html", form=form, is_edit=True, post_id=post_id)


# TODO: delete_post() to remove a blog post from the database
@app.route("/delete-post/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    except Exception as e:
        db.session.rollback()
        return jsonify(error={"failure Something went wrong": str(e)}), 500


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5004)
