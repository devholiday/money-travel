from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
from forms.comment import CommentForm

class BanknoteForm(CommentForm):
    iso_code = SelectField('Currency', default='RUB', coerce=str)
    number = StringField('Number', validators=[DataRequired(), Length(min=1, max=25)])
    denomination = IntegerField('Denomination', validators=[DataRequired(), NumberRange(min=0, max=1000000)])