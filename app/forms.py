from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from app.models import User
from flask import flash

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username", "class": "input"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password", "class": "input"})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = username.data.lower()
        existing_user_username = User.query.filter_by(username=user).first()
        if existing_user_username:
            flash('That username already exists. Please choose a different one.')
            raise ValidationError('That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"autocomplete": "username", "id": "login__username", "type": "text", "class": "form__input", "placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"id": "login__password", "type": "password", "class": "form__input", "placeholder": "Password"})
    submit = SubmitField('Login')