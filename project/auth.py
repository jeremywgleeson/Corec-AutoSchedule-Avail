from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user, login_user
from .models import User
from .forms import SignupForm
from .forms import LoginForm
from .extensions import db, bootstrap
from .keyAuth import check_key, use_key
from .boiler_key import get_hotp_secret, check_credentials, generate_password

import requests
import pyotp

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        print("validated form")
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth.login'))

    return render_template('login.html', form=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user is None:
            # key test before hotp usage (check_key returns none on success)
            key_status = check_key(form.key.data)
            if not key_status:
                # hotp secret test before user creation
                hotp_secret = get_hotp_secret(form.link.data)
                if hotp_secret:
                    if check_credentials(form.username.data, generate_password(hotp_secret, 0, form.pin.data)):
                        # use_key returns true on success and false
                        if use_key(form.key.data, form.username.data):
                            user = User(
                                username=form.username.data,
                                hotp_secret=hotp_secret,
                                counter=1,
                                pin=form.pin.data
                            )
                            user.set_password(form.password.data)
                            db.session.add(user)
                            db.session.commit()  # Create new user
                            login_user(user, remember=True)  # Log in as newly created user
                            return redirect(url_for('main.index'))
                        else:
                            flash("Error using key. Try to use it again.")
                            flash("BoilerKey link used, but registration was not successful. Please get a new link.")
                    else:
                        flash("Incorrect credentials. Please ensure fields are correct.")
                        flash("BoilerKey link used, but registration was not successful. Please get a new link.")
                else:
                    flash("Invalid link. Please get new BoilerKey link.")
            else:
                flash(key_status)
        else:
            flash('A user already exists with that username.')
    return render_template('signup.html', form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
