from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, Length, ValidationError


def length_check(max_length):
    def _length(form, field):
        if len(field.data) > max_length:
            raise ValidationError(f'The input exceeds the maximum length of {max_length} characters.')

    return _length


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
    img_url = StringField(label='Background Img', validators=[
        DataRequired(),
        length_check(250),
        URL(message='Invalid URL format.')])
    body = CKEditorField(label='Main Content', validators=[DataRequired()])
    submit = SubmitField(label="create Post")


class CommentForm(FlaskForm):
    post_id = HiddenField()
    comment = CKEditorField(label='Comment', validators=[DataRequired()])
    submit = SubmitField(label="submit Comment")
