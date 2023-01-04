from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

class BanknoteForm(FlaskForm):        
    iso_code = SelectField('Currency', default='RUB', coerce=str)
    number = StringField('Number', validators=[DataRequired(), Length(min=1, max=25)])
    denomination = IntegerField('Denomination', validators=[DataRequired(), NumberRange(min=0, max=1000000)])
    city = StringField('City', validators=[DataRequired(), Length(min=1, max=50)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=1, max=350)])
    text = StringField('Text', validators=[DataRequired(), Length(min=1, max=550)])