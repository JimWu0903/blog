# create User data table
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Text, ForeignKey

# create the app
app = Flask(__name__)


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blogs.db"

# Create the extension
db = SQLAlchemy(model_class=Base)

# initialize the app with the extension
db.init_app(app)


# CREATE TABLE  默認使用類名的小寫形式作為表名
class User(db.Model):
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


# Create table schema in the database. Requires application context.
with app.app_context():
    db.drop_all()  # 刪除所有表
    db.create_all()  # 創建所有表
