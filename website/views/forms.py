from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from website import db


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Save Changes')


class UpdateFirstNameForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    submit = SubmitField('Update First Name')


class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=150)])
    about_me = TextAreaField('About Me', validators=[Length(max=300)])
    submit = SubmitField('Save Changes')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')