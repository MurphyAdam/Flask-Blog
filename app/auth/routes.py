# -*- coding: utf-8 -*-

from flask import Flask, flash, render_template, request, redirect, url_for, current_app
from validator_collection import validators, checkers, errors
from flask_login import login_required, logout_user, current_user, login_user

from ..forms import signin_validator, signup_validator,\
update_password_validator, reset_password_validator, is_valid_username
from ..models import User
from .. import db
from .email import verify_email, send_password_reset_email
from app.auth import auth





title = "Lang&Code Authentication"


@auth.route('/confirm')
@login_required
def resend_confirmation():
    verify_email(user=current_user)
    flash('A new confirmation email has been sent to you by email. Link validity expires in 1 hour.')
    return redirect(url_for('main.index'))


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    title = "Lang & Code - Reset Password Request" 
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == "GET":
        return render_template('auth/forgot_password.html', title=title)
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                send_password_reset_email(user)
                flash('Check your email for the instructions to reset your password. Link validity expires in 10 mins.')
                return redirect(url_for('main.index'))
            flash('No account with this email was found.')
            return redirect(url_for('main.index'))
        flash('Email not valid')
        return redirect(url_for('main.index'))
    return redirect(url_for('main.index'))


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    title = "Lang & Code - Reset Password"
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if user:
        return render_template('auth/reset_password.html', token=token)
    flash('Your verification token is invalid, has expired or you\
         are not allowed to perform this operation. Operation aborted', 'is-danger')
    return render_template('index.html')


@auth.route('/reset_password_final', methods=['GET', 'POST'])
def reset_password_final():
    title = "Lang & Code - Reset Password Final"
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == "POST":
        token = request.form.get("token")
        password = request.form.get("password")
        confirm_password = request.form.get("passwordConfirmation")
        validate = reset_password_validator(token, password, confirm_password)
        if not validate[0]:
            flash('Your token is invalid/ expired or passwords do not match.', 'is-danger')
            for e in validate[1]:
                flash(e)
            return redirect(url_for("main.index"))
        user = User.verify_reset_password_token(token)
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been reset.', 'is-info')
            return redirect(url_for('main.index'))
        flash('Your verification token is invalid or has expired. Request a fresh one.')
    flash('You are not allowed to access this page', 'is-danger')
    return render_template('index.html')



@auth.route("/signin", methods=["POST", "GET"])
def signin():
    title = "Lang & Code - Sign in"
    if request.method == "GET":
        return render_template("auth/signin.html", title=title)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember_me = request.form.get("rememberMe")
        validate = signin_validator(email, password)
        """
        signin_validator() method validates user signin credits.
        if validation is a success, it returns three objects:
        True, errors, user_to_login
        obj:1: Bolean True: validation is a success
        obj:2: list of errors. In this case an empty list.
        obj:3: a user object: used to login the user.
        if validation fails, it returns two objects:
        obj:1: Bolean False: validation is a failure
        obj:2: list of errors.
        """
        if not validate[0]:
            flash("Sign in system: Your email or password is invalid/ incorrect", "is-danger")
            for e in validate[1]:
                flash(e)
            return redirect(url_for("main.index"))
        user = validate[2]
        current_user = login_user(user, remember=True if remember_me =='on' else False)
        return redirect(url_for('main.index'))
    else:
        flash("Something is not right.", "is-warning")
        return redirect(url_for("main.index"))


@auth.route('/signout')
@login_required
def signout():
    logout_user()
    current_user = None
    return redirect(url_for('main.index'))


@auth.route("/signup", methods=["POST", "GET"])
def signup():
    title = "Lang & Code - Sign up"
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == "GET":
        return render_template("auth/signup.html", title=title)
    if request.method == "POST":
        fullname = request.form.get("fullname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        validate = signup_validator(fullname, username, email, password, password2)
        """
        The signup_validator() method returns two values:
        param:1: Bolean type: True if validation successed, Falske otherwise
        param:2: List type: List of errors in both cases. Empty if Bolean is True.
        """
        if not validate[0]:
            flash("Sign up system: some of your data are invalid", "is-danger")
            for e in validate[1]:
                flash(e)
            return redirect(url_for("main.index"))
        add_user = User(fullname=fullname, username=username, email=email)
        add_user.set_password(password)
        db.session.add(add_user)
        db.session.commit()
        verify_email(user=add_user)
        flash("Your account was successfully created! Please confirm\
                     your account and then sign in", "is-primary")
        return redirect(url_for('main.index'))
    flash("Something went wrong.", "is-danger")
    return redirect(url_for("main.index"))



@auth.route("/confirm_email/<token>", methods=["GET", "POST"])
@login_required
def confirm_email(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
        return redirect(url_for("main.index"))
    flash('The confirmation link is invalid or has expired.')
    return redirect(url_for("main.index"))
