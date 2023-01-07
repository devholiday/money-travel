from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length

class Banknote0Form(FlaskForm):
    iso_code = SelectField('Currency', default='RUB', coerce=str)
    number = StringField('Number', validators=[DataRequired(), Length(min=1, max=25)])