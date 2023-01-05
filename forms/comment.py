from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

class CommentForm(FlaskForm):
    city = StringField('City', validators=[DataRequired(), Length(min=1, max=50)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=1, max=350)])
    text = StringField('Text', validators=[DataRequired(), Length(min=1, max=550)])