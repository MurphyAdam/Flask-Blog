# -*- coding: utf-8 -*-

from datetime import datetime
import json

from flask import current_app, flash, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc, distinct

from app.models import User, Post, \
SavedArticle, AboutUs, SuspenedUser, ContactUs, ReportedUser
from app.admin import admin
from app import db
from app.decorators import admin_required


title = "Lang & Code - Admin"


@admin.route("/users/<int:id>/change_role", methods=["GET", "POST"])
@login_required
@admin_required
def user_change_role(id):
    title = "Users - Change Role"
    if current_user.is_authenticated and current_user.is_admin():
        if request.method == "GET" and id:
            user = User.query.get(id)
            if user:
                return render_template("admin/change_role.html", user=user)
            flash('User not found')
            return redirect(url_for("main.index"))
        if request.method == "POST":
            role_id = request.form.get("roleId")
            master_password = request.form.get("masterPassword")
            if role_id and id and current_user.check_master_password(master_password):
                user = User.query.get(id)
                if user:
                    user.role = role_id
                    db.session.commit()
                    flash('Successfully changed user role')
                    return redirect(url_for('main.users'))
                flash('User not found')
                return redirect(url_for("main.index"))
            flash('Either user role id or the master password is invalid')
            return redirect(url_for("main.index"))
    flash("You do not have permission to view this page.", "is-danger")
    return redirect(url_for("main.index"))


@admin.route("/users/<int:id>/delete", methods=["GET", "POST"])
@login_required
@admin_required
def delete_user(id):
    title = "Users - Delete user"
    if current_user.is_authenticated and current_user.is_admin():
        if request.method == "GET" and id:
            user = User.query.get(id)
            if user:
                return render_template("admin/delete_user.html", user=user, title=title)
            flash('User not found')
            return redirect(url_for("main.index"))
        if request.method == "POST":
            master_password = request.form.get("masterPassword")
            if id and current_user.check_master_password(master_password):
                user = User.query.get(id)
                if user:
                    db.session.delete(user)
                    db.session.commit()
                    flash('Successfully deleted user')
                    return redirect(url_for('main.users'))
                flash('User not found')
                return redirect(url_for("main.index"))
            flash('Either user or the master password is invalid')
            return redirect(url_for("main.index"))
    flash("You do not have permission to view this page.", "is-danger")
    return redirect(url_for("main.index"))


@admin.route("/users/<int:id>/suspend", methods=["GET", "POST"])
@login_required
@admin_required
def suspend_user(id):
    title = "Users - Suspend user"
    if current_user.is_authenticated and current_user.is_admin():
        if request.method == "GET" and id:
            user = User.query.get(id)
            if user:
                if user != current_user:
                    return render_template("admin/suspend_user.html", user=user, title=title)
                flash("Cannot suspend yourself")
                return redirect(url_for("main.index"))
            flash('User not found')
            return redirect(url_for("main.index"))
        if request.method == "POST":
            master_password = request.form.get("masterPassword")
            note = request.form.get("note")
            if id:
                user = User.query.get(id)
                if user:
                    if user != current_user:
                        user.account_state = 0
                        suspend_user = SuspenedUser(user_id=id, note=note if note else None)
                        db.session.add(suspend_user)
                        db.session.commit()
                        flash('Successfully suspended user')
                        return redirect(url_for('main.users'))
                    flash("Cannot suspend yourself")
                    return redirect(url_for("main.index"))
                flash('User not found')
                return redirect(url_for("main.index"))
            flash('Either user or the master password is invalid')
            return redirect(url_for("main.index"))
    flash("You do not have permission to view this page.", "is-danger")
    return redirect(url_for("main.index"))


@admin.route("/users/<int:id>/unsuspend", methods=["GET", "POST"])
@login_required
@admin_required
def unsuspend_user(id):
    title = "Users - Unsuspend user"
    if current_user.is_authenticated and current_user.is_admin():
        if request.method == "GET" and id:
            user = User.query.get(id)
            if user:
                return render_template("admin/unsuspend_user.html", user=user, title=title)
            flash('User not found')
            return redirect(url_for("main.index"))
        if request.method == "POST":
            master_password = request.form.get("masterPassword")
            if id and current_user.check_master_password(master_password):
                user = User.query.get(id)
                if user:
                    user.account_state = 1
                    db.session.commit()
                    flash('Successfully unsuspended user')
                    return redirect(url_for('main.users'))
                flash('User not found')
                return redirect(url_for("main.index"))
            flash('Either user or the master password is invalid')
            return redirect(url_for("main.index"))
    flash("The current action cannot be performed with the requested method", "is-danger")
    return redirect(url_for("main.index"))

@admin.route("/contact_us/show/all")
@login_required
@admin_required
def show_contactus_messages():
    title = "Contact us - Show All"
    if current_user.is_authenticated and current_user.is_admin():
        page = request.args.get('page', 1, type=int)
        contacts = ContactUs.query.order_by(ContactUs.contact_date.asc()).paginate(
        page, 10, False)
        if contacts:
            return render_template("admin/show_contactus_messages.html", 
                contacts=contacts.items, 
                pagination=contacts,
                title=title)
        flash("No new contacts seem to exist.", "is-info")
        return redirect(url_for("main.control"))
    flash("Access denied")
    return redirect(url_for("main.index"))


@admin.route("/contact_us/<int:id>/show")
@login_required
@admin_required
def show_contactus_message(id):
    title = "Contact us - Show #{}".format(id)
    if current_user.is_authenticated and current_user.is_admin():
        contact = ContactUs.query.get(id)
        if contact:
            return render_template("admin/show_contactus_message.html", 
                contact=contact,
                title=title)
        flash(f"No text with the id {id} seems to exist in the corpus.", "is-info")
        return redirect(url_for("admin.control"))
    flash("Access denied")
    return redirect(url_for("main.index"))