from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import DataRequired, Length

class SearchForm(FlaskForm):
    q = StringField('', validators=[DataRequired(), Length(min=3, max=50)])
    filter = RadioField('', default='number')