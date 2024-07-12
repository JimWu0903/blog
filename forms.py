from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class RegisterForm(FlaskForm):
    name = StringField(label='User Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired()])
    password = StringField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Join Us!")


class PostForm(FlaskForm):
    title = StringField(label='Post Title', validators=[DataRequired()])
    subtitle = StringField(label='Subtitle', validators=[DataRequired()])
    # author = StringField(label='Author', validators=[DataRequired()])
    img_url = StringField(label='Background Img', validators=[DataRequired()])
    body = CKEditorField(label='Main Content', validators=[DataRequired()])
    submit = SubmitField(label="create Post")


class CommentForm(FlaskForm):
    post_id = HiddenField()
    comment = CKEditorField(label='Comment', validators=[DataRequired()])
    submit = SubmitField(label="submit Comment")
