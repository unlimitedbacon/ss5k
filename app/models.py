from app import db
from datetime import datetime
from hashlib import md5
import bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), index=True, unique=True, nullable = False)
    password = db.Column(db.String)
    created = db.Column(db.DateTime)
    passwordReset = db.Column(db.String(128))
    passwordResetExpiry = db.Column(db.DateTime)
    cars = db.relationship('Car')
    last_seen = db.Column(db.DateTime)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % ( md5(self.email.encode('utf-8')).hexdigest(), size )

    def __init__(self, email, password):
        self.email = email
        self.created = datetime.now()
        self.set_password(password)

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

junkyard_car_links = db.Table('junkyard_car_links',
        db.Column('car_id', db.Integer, db.ForeignKey('car.id'), primary_key=True),
        db.Column('junkyard_id', db.Integer, db.ForeignKey('junkyard.id'), primary_key=True)
        )

class Car(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    make = db.Column(db.String)
    model = db.Column(db.String)
    years = db.Column(db.String)
    yards = db.relationship('Junkyard',
                            secondary=junkyard_car_links,
                            back_populates='cars')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, make, model, years, yards, user):
        self.make = make
        self.model = model
        self.years = ','.join(years)
        self.user_id = user.id
        for yard in yards:
            yard_id = int(yard)
            self.yards.append( Junkyard.query.get(yard_id) )

    def __repr__(self):
        return '<Car %r>' % (self.id)

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
    cars = db.relationship('Car',
                           secondary=junkyard_car_links,
                           back_populates='yards')

    def __init__(self, code, state, city):
        self.code = code
        self.country = 'USA'
        self.state = state
        self.city = city
        self.company = 'LKQ'
        self.name = 'Pick Your Part'

    def __repr__(self):
        return '<Junkyard %r %r %r>' % (self.code, self.state, self.city)

