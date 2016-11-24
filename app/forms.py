from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import Required, Length, Email
from app.models import User, Junkyard

car_year_options = []
for year in range(datetime.now().year,1886,-1):
    car_year_options.append( (str(year),str(year)) )

junkyard_options = []
for yard in Junkyard.query.all():
    junkyard_options.append( (str(yard.id),str("%s - %s" % (yard.state,yard.city))) )

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 256), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 256), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in', default=False)
    submit = SubmitField('Log In')

class AddCarForm(FlaskForm):
    make = StringField('make')
    model = StringField('model')
    years = SelectMultipleField('years', choices=car_year_options)
    yards = SelectMultipleField('yards', choices=junkyard_options)
    submit = SubmitField('Add Car')

    def __init__(self, car=None, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.car = car

class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[Required()])
    about_me = TextAreaField('about_me', validators=[Length(0,140)])

    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True
