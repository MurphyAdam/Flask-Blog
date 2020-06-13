# -*- coding: utf-8 -*-

from datetime import datetime

from flask_login import login_required, current_user
from sqlalchemy import desc
from flask import current_app, flash, render_template, request, redirect, url_for, jsonify, g
from validator_collection import validators, checkers, errors

from ..models import User, Post, Category, \
SavedArticle, Tag, AboutUs, ContactUs, load_user
from ..data_retrieval import latest_added_articles
from .email import contact_us_send_email
from ..decorators import admin_required, account_state
from .. import db
from ..forms import is_valid_username
from app.main import main



title = "Lang & Code - Home"


@main.before_app_request
@account_state
def before_request():
    if request.accept_mimetypes['text/html'] > request.accept_mimetypes['application/json']:
        tags = Tag.query.all()
        categories = Category.query.all()
        g.tags = tags
        g.categories = categories
        if current_user.is_authenticated:
            if not current_user.confirmed:
                g.confirm_account = "Please access your email and confirm your account."
    else:
        g.tags = None
        g.categories = None
    current_user.last_seen = datetime.utcnow()
    db.session.commit()


##########################  APP ############################
##################################################################
@main.route("/")
def index():
    if current_user.is_authenticated:
        latest_articles = latest_added_articles(1)
        latest_articles_list = latest_added_articles(5)
        # for tags, we use the global g.tags defined in the before_request
        return render_template("authenticated_index.html", 
                                title=title,
                                latest_articles=latest_articles, 
                                latest_articles_list=latest_articles_list,
                                tags=g.tags)
    return render_template("default_index.html", title=title)


@main.route("/users", methods=["GET", "POST"])
@login_required
def users():
    title = "Lang & Code - Users"
    page = request.args.get('page', 1, type=int)
    if request.method == "GET":
        current_user.last_follower_view_time = datetime.utcnow()
        db.session.commit()
        users = User.query.paginate(
        page, current_app.config['USERS_PER_PAGE'], False)
        return render_template("users.html", 
            users=users.items, 
            pagination=users,
            title=title)
    return render_template("users.html", title=title)


@main.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    title = "Lang & Code - Contact us"
    if request.method == "POST":
        subject = request.form.get("subject")
        body = request.form.get("body")
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        is_user = User.query.filter_by(email=email).first()
        if subject and body and email and fullname:
            contact_us_send_email(subject, body, email, fullname)
            if is_user:
                contact_us = ContactUs(is_user=True, 
                    user_id=is_user.id, 
                    subject=subject,
                    seen=False, 
                    body=body)
                db.session.add(contact_us)
                db.session.commit()
            elif not is_user:
                contact_us = ContactUs(is_user=False, 
                    seen=False, 
                    fullname=fullname,
                    email=email, 
                    subject=subject,
                    body=body)
                db.session.add(contact_us)
                db.session.commit()
            flash('Thank you for contacting us. You will hear from us once we get to your email.')
            return redirect(url_for('main.index'))
        flash("All the inputs must be filled.", "is-danger")
        return redirect(url_for("main.index"))
    if request.method == "GET":
        return render_template("contact_us.html", title=title)
    flash("Something went wrong.", "is-warning")
    return redirect(url_for("main.index"))


@main.route("/report_bug", methods=["GET", "POST"])
def report_bug():
    title = "Lang & Code - Report Bug"
    if request.method == "POST":
        subject = request.form.get("subject")
        body = request.form.get("body")
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        if subject and body and email and fullname:
            contact_us_send_email(subject, body, email, fullname)
            flash('Thank you for contacting us. You will hear from us once we get to your email.')
            return redirect(url_for('main.index'))
        flash("All the inputs must be filled.", "is-danger")
        return redirect(url_for("main.index"))
    if request.method == "GET":
        return render_template("contact_us.html", title=title)
    flash("Something went wrong.", "is-warning")
    return redirect(url_for("main.index"))
