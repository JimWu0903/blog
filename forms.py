from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, Length, ValidationError
from model import BlogPost


def length_check(max_length):
    def _length(form, field):
        """
        自定義驗證方法是由Form類調用的。當這些方法被調用時，它們會自動接收兩個參數：form和field。

        form參數是對整個表單實例的引用。
        field參數是對當前正在驗證的特定字段的引用。
        """
        if len(field.data) > max_length:
            raise ValidationError(f'The input exceeds the maximum length of {max_length} characters.')

    return _length


def unique_title(form, field):
    if BlogPost.query.filter_by(title=field.data).first():
        raise ValidationError('A post with this title already exists. Please choose a different title.')


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
    title = StringField(label='Post Title', validators=[
        DataRequired(),
        unique_title])
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
