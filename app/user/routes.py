# -*- coding: utf-8 -*-

from datetime import datetime
import json

from flask_login import login_required, current_user, fresh_login_required
from sqlalchemy import desc
from flask import current_app, flash, render_template, request, redirect, url_for, jsonify
from validator_collection import validators, checkers, errors

from ..models import User, Post, SavedArticle, load_user, DeletedAccount
from ..decorators import admin_required
from .. import db
from ..forms import is_valid_username, update_password_validator
from .. functions import contains_swear_words
from app.user import user



title = "Lang & Code - Home"



@user.route("/myazoul")
@login_required
def myazoul():
    title = "Lang & Code - My Azoul"
    if current_user.is_authenticated:
        saved_articles = current_user.saved_articles.order_by(SavedArticle.date_saved.desc()).limit(5).all()
        my_articles = current_user.articles.order_by(Post.pub_date.desc()).limit(5).all()
        followed = current_user.followed.limit(20).all()
        followers = current_user.followers.limit(20).all()
        return render_template("myazoul.html", 
            title=title, 
            saved_articles=saved_articles, 
            my_articles=my_articles, 
            followed=followed, 
            followers=followers)
    flash("You do not have permission to view this page.", "is-danger")
    return redirect(url_for("main.index"))


@user.route("/myazoul/saved_articles")
@login_required
def myazoul_saved_articles():
    title = "Lang & Code - My Azoul: Saved Articles"
    page = request.args.get('page', 1, type=int)
    saved_articles = current_user.saved_articles.order_by(SavedArticle.date_saved.asc()).paginate(
        page, current_app.config['SAVED_ARTICLES_PER_PAGE'], False)
    return render_template("myazoul/saved_articles.html", 
        saved_articles=saved_articles.items,
        pagination=saved_articles,
        title=title)


@user.route("/myazoul/my_articles")
@login_required
@admin_required
def myazoul_my_articles():
    title = "Lang & Code - My Azoul: My Articles"
    page = request.args.get('page', 1, type=int)
    my_articles = current_user.articles.order_by(Post.pub_date.asc()).paginate(
        page, current_app.config['MY_ARTICLES_PER_PAGE'], False)
    return render_template("myazoul/my_articles.html", 
        my_articles=my_articles.items,
        pagination=my_articles,
        title=title)


@user.route("/myazoul/followed")
@login_required
@admin_required
def myazoul_followed():
    title = "Lang & Code - My Azoul: Followed users"
    page = request.args.get('page', 1, type=int)
    followed = current_user.followed.paginate(
        page, current_app.config['FOLLOWING_PER_PAGE'], False)
    return render_template("myazoul/followed.html", 
        followed=followed.items,
        pagination=followed,
        title=title)


@user.route("/myazoul/followers")
@login_required
@admin_required
def myazoul_followers():
    title = "Lang & Code - My Azoul: Followed users"
    page = request.args.get('page', 1, type=int)
    followers = current_user.followers.paginate(
        page, current_app.config['FOLLOWERS_PER_PAGE'], False)
    return render_template("myazoul/followers.html", 
        followers=followers.items,
        pagination=followers,
        title=title)


@user.route('/notifications/all')
@login_required
def all_notifications():
    title = "Lang & Code - All Notifications"
    page = request.args.get('page', 1, type=int)
    current_user.last_message_read_time = datetime.utcnow()
    notifications = current_user.notifications.order_by(Notification.date.desc()).paginate(
        page, current_app.config['ALL_NOTIFICATIONS_PER_PAGE'], False)
    current_user.set_all_notifications_to_seen()
    db.session.commit()
    return render_template('user/notifications.html', 
        notifications=notifications.items,
        pagination=notifications,
        title=title)


@user.route('/notifications/all/get')
@login_required
def get_all_notifications():
    notifications = current_user.notifications.filter_by(seen=False).order_by(Notification.date.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'date': n.date
    } for n in notifications])



@user.route('/notifications')
@login_required
def notifications():
    notifications = current_user.notifications.filter_by(seen=False).count()
    if notifications == 0:
        return jsonify({'notification_number':''})
    return jsonify({'notification_number':notifications})


@user.route("/<id>/profile", methods=["GET", "POST"])
@login_required
def profile(id):
    current_url = "profile"
    title = "Lang & Code - Profile"
    if current_user.is_authenticated and request.method == "GET":
        if id:
            if current_user.id == id:
                return render_template("profile.html", 
                    title=title, 
                    user=current_user, 
                    current_url=current_url)
            user = User.query.get(id)
            if user:
                return render_template("profile.html", 
                    title=title, 
                    user=user, 
                    current_url=current_url)
            flash("The user you are looking for does not seem to exist.")
            return render_template("profile.html", 
                title=title, 
                user=current_user, 
                current_url=current_url)
        return render_template("profile.html", title=title, user=current_user)
    flash("You must be logged in to access the page you requested." , "is-danger")
    return redirect(url_for('main.index'))


@user.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    current_url = "settings"
    title = "Lang & Code - Account Settings"
    return render_template("user/settings.html", title=title)

@user.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    title = "Lang & Code - Edit Profile"
    if request.method == "POST":
        _csrf_token = request.form.get("_csrf_token")
        username = request.form.get("username")
        about_me = request.form.get("aboutMe")
        print(username, about_me)
        if username is not None and username != current_user.username:
            if is_valid_username(username):
                if contains_swear_words(username):
                    return jsonify(message='- You cannot use swear words in your username.', codename=0)
                new_username = User.query.filter_by(username=username).first()
                if new_username:
                    return jsonify(message='- A user already exist with this username.', codename=0)
                else:
                    current_user.username = username
                    current_user.about_me = about_me
                    db.session.commit()
                    return jsonify(message='- Your changes have been saved.', 
                        codename=1)
            return jsonify(message='- Username is invalid. ' 
                'Usernames must be 4 characters minimum and must have only letters, numbers, dots or underscores', codename=0)
        if about_me and checkers.is_string(about_me):
            if contains_swear_words(about_me):
                return jsonify(message='- You cannot use swear words in your bio.', codename=0)
            if len(about_me) > 200:
                return jsonify(message='- Your About Me must not execeed 200 characters.')
            current_user.about_me = about_me
            db.session.commit()
            return jsonify(message='- Your changes have been saved.', codename=1)
        return jsonify(message='- Please verify your inputs', codename=0)
    flash("You must be logged in to access the page you requested." , "is-danger")
    return redirect(url_for('main.index'))


@user.route('/<int:id>/follow', methods=["GET"])
@login_required
def follow(id):
    user = User.query.get(id)
    if user is None:
        return jsonify(message='Not found.')
    if user == current_user:
        return jsonify(message='Cannot follow self')
    if current_user.is_following(user):
        return jsonify(message='Already following')

    current_user.follow(user)
    db.session.commit()
    return jsonify(message='Following')


@user.route('/<int:id>/unfollow', methods=["GET"])
@login_required
def unfollow(id):
    user = User.query.get(id)
    if user is None:
        return jsonify(message='Not found.')
    if user == current_user:
        return jsonify(message='Cannot unfollow self')
    current_user.unfollow(user)
    db.session.commit()
    return jsonify(message='Unfollowed')



@user.route('/update_password', methods=['GET', 'POST'])
@login_required
@fresh_login_required
def update_password():
    title = "Lang & Code - Update Account"
    if request.method == "GET":
        return render_template("user/update_password.html", title=title)
    if request.method == "POST":
        current_password = request.form.get("currentPassword")
        new_password = request.form.get("newPassword")
        confirm_new_password = request.form.get("newPasswordConfirmation")
        validate = update_password_validator(current_password, new_password, confirm_new_password)
        if not validate[0]:
            flash('Your password is invalid or do not match. Please try again.', 'is-danger')
            for e in validate[1]:
                flash(e)
            return redirect(url_for("main.index"))
        current_user.set_password(new_password)
        db.session.commit()
        flash('Your password has been updated.', 'is-info')
        return redirect(url_for('main.index'))
    flash('To protect your account, you must re-authenticate to update your password.', 'is-info')
    return render_template('index.html')


@user.route("/delete_account", methods=["POST", "GET"])
@login_required
@fresh_login_required
def delete_account():
    title = "Lang & Code[!] - Delete Account"
    if request.method == "GET":
        flash("Warning: You are about to delete your account. Once deleted, it cannot be recovered.", "is-danger")
        return render_template("user/delete_account.html", title=title)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        reason = request.form.get("reason")
        if email and password and email == current_user.email and current_user.check_password(password):
            deleted_account = DeletedAccount(email=email, reason=reason if checkers.is_string(reason) else None)
            db.session.add(deleted_account)
            db.session.delete(current_user)
            db.session.commit()
            flash("Account system: Your Account and all the data related to it have been deleted.", "is-danger")
            return redirect(url_for("main.index"))
        flash("Account system: Your email or password is invalid", "is-danger")
        return redirect(url_for("main.index"))
    flash('Something went wrong, or you do not have enough permission to perform this action.')
    return redirect(url_for('main.index'))


@user.route("/<int:id>/report_user", methods=["GET", "POST"])
@login_required
def report_user(id):
    title = "Lang & Code - Report User"
    if request.method == "POST":
        subject = request.form.get("subject")
        body = request.form.get("body")
        if subject and body and id:
            user = User.query.get(id)
            if user:
                current_user.report(user, subject, body)
                db.session.commit()
                flash('Thank you for reporting. We will review your report once we get to it.')
                return redirect(url_for('main.index'))
            flash('User with id not found.')
            return redirect(url_for("main.index"))
        flash("All the inputs must be filled.", "is-danger")
        return redirect(url_for("main.index"))
    if request.method == "GET" and id:
        user = User.query.get(id)
        if user:
            return render_template("report_user.html", user=user, title=title)
        flash('User with id not found.')
        return redirect(url_for("main.index"))
    flash("All the inputs must be filled.", "is-danger")
    return redirect(url_for("main.index"))