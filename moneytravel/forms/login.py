from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('', validators=[DataRequired(), Length(min=3, max=255)])
    password = PasswordField('', validators=[DataRequired(), Length(min=3, max=255)])