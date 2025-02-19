from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Create Account")

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    rating = RadioField('Rating', choices=[(str(i), '⭐' * i) for i in range(1, 6)], validators=[DataRequired()])
    submit = SubmitField('Post')
