from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from website import db
from website.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')


class UpdateFirstNameForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    submit = SubmitField('Update First Name')

    def validate_first_name(self, field):
        # Check if the new first name is already taken
        existing_user = User.query.filter_by(first_name=self.first_name.data).first()
        if existing_user and existing_user.id != current_user.id:
            raise ValidationError('This first name is already taken. Please choose a different one.')

    # def __init__(self, original_first_name, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.original_first_name = original_first_name
    #
    # def validate_username(self, first_name):
    #     if first_name.data != self.original_username:
    #         user = db.session.scalar(db.select(User).where(
    #             User.first_name == self.first_name.data))
    #         if user is not None:
    #             raise ValidationError('Please use a different username.')



class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=150)])
    about_me = TextAreaField('About Me', validators=[Length(max=300)])
    submit = SubmitField('Save Changes')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
