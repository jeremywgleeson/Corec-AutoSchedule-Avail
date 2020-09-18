from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, Regexp

class SignupForm(FlaskForm):
    """User Sign-up Form."""

    username = StringField(
        'Purdue Username',
        validators=[
            Length(min=3),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, message='Select a stronger password.')
        ]
    )
    confirm = PasswordField(
        'Confirm Your Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    link = StringField(
        'Link',
        validators=[
            DataRequired(),
            Regexp("(https:\/\/)?m-1b9bef70\.duosecurity\.com\/activate\/.{20}", message="Invalid link. Visit https://www.purdue.edu/apps/account/BoilerKey/ and add a new device (name does not matter). Continue until you see a qr code, then copy the link below the qr code here.")
        ],
        description="Visit https://www.purdue.edu/apps/account/BoilerKey/ and add a new device (name does not matter). Continue until you see a qr code, then copy the link below the qr code here."
    )
    key = StringField('Invite Key', validators=[DataRequired()])
    pin = StringField('Pin', validators=[
        DataRequired(),
        Regexp("\d{4}", message="Enter 4 digit pin used for Purdue login")
        ]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """User Log-in Form."""
    username = StringField('Purdue Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
