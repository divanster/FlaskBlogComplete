from flask import Blueprint, render_template, flash, redirect, url_for
from website import db
from website.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from website.auth.forms import (SignupForm, LoginForm, ChangePasswordForm, UpdateFirstNameForm,
                                ResetPasswordRequestForm, ResetPasswordForm)
from datetime import date, datetime
from website.auth import auth
from website.auth.email import send_password_reset_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash('Logged in successfully!', category='success')
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect email or password.', category='error')

    return render_template("login.html", user=current_user, form=form)


@auth.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignupForm()

    if form.validate_on_submit():
        email = form.email.data
        first_name = form.first_name.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        else:
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password, method='pbkdf2:sha256'))
            new_user.date = datetime.now()  # Set the 'date' attribute to the current date
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            login_user(new_user)
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", form=form, user=current_user)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_password = form.old_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        # Check if the old password matches the user's current password
        if not check_password_hash(current_user.password, old_password):
            flash('Incorrect old password.', category='error')
        else:
            # Update the user's password
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            flash('Password changed successfully!', category='success')

    return render_template('change_password.html', form=form, user=current_user)


@auth.route('/update-first-name', methods=['GET', 'POST'])
@login_required
def update_first_name():
    form = UpdateFirstNameForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.first_name = form.first_name.data
        db.session.commit()
        flash('Your first name has been updated!', 'success')
        return redirect(url_for('views.blogpost'))
    return render_template('update_first_name.html', title='Update First Name', form=form, user=current_user)


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html', title='Reset Password',
                           form=form, user=current_user)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('views.home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('email/reset_password.html',
                           form=form, user=current_user)
