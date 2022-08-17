from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import InputRequired, Email, EqualTo, email_validator

class LoginForm(FlaskForm):
    email = StringField('Fullname', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    full_name = StringField('Fullname', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class GroupForm(FlaskForm):
    group_name = StringField('Group Name', validators=[InputRequired()])
    budget = StringField('Budget', validators=[InputRequired()])
    date = StringField('Date', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    group_pic = FileField('Group Image', validators=[InputRequired()])
    submit = SubmitField('Create Group')

class JoinForm(FlaskForm):
    join_code = StringField('Join Code', validators=[InputRequired()])
    submit = SubmitField('Join Group')
    