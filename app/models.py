from app import db
from datetime import datetime, timedelta
from hashlib import md5
import bcrypt
import os
import base64

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), index=True, unique=True, nullable = False)
    password = db.Column(db.String)
    created = db.Column(db.DateTime)
    confirmed = db.Column(db.Boolean)
    confirmation = db.Column(db.String)
    passwordReset = db.Column(db.String)
    passwordResetExpiry = db.Column(db.DateTime)
    wanted_cars = db.relationship('WantedCar')
    last_seen = db.Column(db.DateTime)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
        print(self.password)

    def reset_password(self):
        self.passwordReset = base64.b32encode(os.urandom(20)).decode('utf-8')
        self.passwordResetExpiry = datetime.now() + timedelta(days=1)

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % ( md5(self.email.encode('utf-8')).hexdigest(), size )

    def __init__(self, email, password):
        self.email = email
        self.created = datetime.now()
        self.set_password(password)
        self.confirmed = False
        self.confirmation = base64.b32encode(os.urandom(20)).decode('utf-8')

    def __repr__(self):
        return '<User %r>' % (self.email)

    # Flask_login stuff
    # Whether or not the user is allowed to authenticate
    @property
    def is_authenticated(self):
        return True

    # Whether or not the user is banned
    @property
    def is_active(self):
        return True

    # Whether or not this is an actual user or
    # the default (not logged in) user
    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id) # Python 2
        except NameError:
            return str(self.id)     # Python 3

junkyard_wantedcar_links = db.Table('junkyard_wantedcar_links',
        db.Column('wantedcar_id', db.Integer, db.ForeignKey('wanted_car.id'), primary_key=True),
        db.Column('junkyard_id', db.Integer, db.ForeignKey('junkyard.id'), primary_key=True)
        )

class WantedCar(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    make = db.Column(db.String)
    model = db.Column(db.String)
    color = db.Column(db.String)
    years = db.Column(db.String)
    yards = db.relationship('Junkyard',
                            secondary=junkyard_wantedcar_links,
                            back_populates='wanted_cars',
                            order_by='Junkyard.state, Junkyard.city')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, make, model, color, years, yards, user):
        self.make = make
        self.model = model
        self.color = color
        self.years = ', '.join(years)
        self.user_id = user.id
        for yard in yards:
            yard_id = int(yard)
            self.yards.append( Junkyard.query.get(yard_id) )

    def __repr__(self):
        return '<WantedCar %r %r %r>' % (self.id, self.make, self.model)

    def list_yards(self):
        ylist = [y.city for y in self.yards]
        return ", ".join(ylist)

class Junkyard(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    code = db.Column(db.Integer)
    country = db.Column(db.String)
    state = db.Column(db.String)
    city = db.Column(db.String)
    company = db.Column(db.String)
    name = db.Column(db.String)
    cars = db.relationship('Car')
    wanted_cars = db.relationship('WantedCar',
                           secondary=junkyard_wantedcar_links,
                           back_populates='yards',
                           lazy='subquery')

    # Get a list of other wanted cars with similar criteria
    def match_searches(self, w):
        matches = []
        for c in self.wanted_cars:
            if c.make.lower() == w.make.lower() and c.model.lower() == w.model.lower() and c.color.lower() == w.color.lower():
                matches.append(c)
        return matches

    def __init__(self, code, state, city):
        self.code = code
        self.country = 'USA'
        self.state = state
        self.city = city
        self.company = 'LKQ'
        self.name = 'Pick Your Part'

    def __repr__(self):
        return '<Junkyard %r %r %r>' % (self.code, self.state, self.city)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String, index=True)
    image = db.Column(db.String)
    imglink = db.Column(db.String)
    make = db.Column(db.String)
    model = db.Column(db.String)
    year = db.Column(db.String)
    arrival_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    yard_id = db.Column(db.Integer, db.ForeignKey('junkyard.id'))
    last_seen = db.Column(db.DateTime)
    
    def __init__(self, yard):
        self.yard_id = yard.id

    def __repr__(self):
        return '<Car %r %r %r %r>' % (self.year, self.make, self.model, self.id)
