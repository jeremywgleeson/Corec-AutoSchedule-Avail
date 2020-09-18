from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import base64

class User(UserMixin, db.Model):

    # __tablename__ = 'flasklogin-users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.String(200),
        primary_key=False,
        unique=False,
        nullable=False
	)
    hotp_secret = db.Column(
        db.String(20),
        primary_key=False,
        unique=False,
        nullable=False
    )
    counter = db.Column(
        db.Integer,
        primary_key=False,
        unique=False,
        nullable=False
    )
    pin = db.Column(
        db.Integer,
        primary_key=False,
        unique=False,
        nullable=False
    )
    # reference to reservations table
    reservations = db.relationship(
        'Reservation',
        backref=db.backref('user', lazy='joined'),
        cascade="all, delete-orphan",
        lazy=True
    )

    # reference to repeating reservations table
    repeating_reservations = db.relationship(
        'RepeatingReservation',
        backref=db.backref('user', lazy='joined'),
        cascade="all, delete-orphan, delete",
        lazy=True
    )

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def get_login_pass(self):
        """Generate login pass for purdue sites"""
        hotp = pyotp.HOTP(base64.b32encode(self.hotp_secret.encode()))

        hotpPassword = hotp.at(self.counter)

        self.counter += 1

        password = "{},{}".format(self.pin, hotpPassword)

        return password


    def __repr__(self):
        return '<User {}>'.format(self.username)

class Reservation(db.Model):
    # __tablename__ = 'reservation-events'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    start_time = db.Column(
        db.DateTime,
        primary_key=False,
        unique=False,
        nullable=False
    )
    end_time = db.Column(
        db.DateTime,
        primary_key=False,
        unique=False,
        nullable=False
	)
    repeating_weekly = db.Column(
        db.Boolean,
        primary_key=False,
        unique=False,
        nullable=False
    )
    # use enum for this, dont know where to define though
    #   0 = queued
    #   1 = success
    #   2 = failed
    #   3 = deleted
    status = db.Column(
        db.Integer,
        primary_key=False,
        unique=False,
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    def __repr__(self):
        return '<Reservation {}>'.format(self.start_time.strftime("%m/%d/%Y, %H:%M:%S"))

class RepeatingReservation(db.Model):
    # __tablename__ = 'reservation-events'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    start_time = db.Column(
        db.DateTime,
        primary_key=False,
        unique=False,
        nullable=False
    )
    end_time = db.Column(
        db.DateTime,
        primary_key=False,
        unique=False,
        nullable=False
	)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    def __repr__(self):
        return '<RepeatingReservation {} {}>'.format(self.weekday, self.start_time.strftime("%H:%M:%S"))
