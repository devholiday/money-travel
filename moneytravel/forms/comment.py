from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    city = StringField('City', validators=[DataRequired(), Length(min=1, max=50)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=1, max=350)])
    text = StringField('Text', validators=[DataRequired(), Length(min=1, max=550)])