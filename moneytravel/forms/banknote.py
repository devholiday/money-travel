from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange
from moneytravel.forms.comment import CommentForm

class BanknoteForm(CommentForm):
    denomination = IntegerField('Denomination', validators=[DataRequired(), NumberRange(min=0, max=1000000)])