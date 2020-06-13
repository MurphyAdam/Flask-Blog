from functools import wraps
import datetime
from flask import (abort, url_for, redirect, render_template, flash, g, 
					session, request, make_response, current_app)

from flask_login import current_user, logout_user
from werkzeug.exceptions import Unauthorized

from app import moment
from app.functions import format_time


def permission_required():
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if current_user.is_authenticated:
				if not current_user.is_admin():
					abort(403)
			return f(*args, **kwargs)
		return decorated_function
	return decorator


def admin_required(f):
	return permission_required()(f)


def account_confirmed(func):
	@wraps(func)
	def decorated_function(*args, **kwargs):
		if current_user.is_authenticated:
			if not current_user.confirmed:
				abort(401)
		return func(*args, **kwargs)
	return decorated_function



def account_state(func):
	@wraps(func)
	def decorated_function(*args, **kwargs):
		if current_user.is_authenticated:
			if not current_user.has_valid_account_state():
				if request.environ['PATH_INFO'] == '/auth/signout':
					logout_user()
					if request.environ['QUERY_STRING'] == 'contact_us':
						return redirect(url_for("main.contact_us"))
					return redirect(url_for("main.index"))
				suspension = current_user.suspension.first()
				return render_template("errors/blocked_account.html", 
					user=current_user, 
					note=suspension.note, 
					date=format_time(suspension.date_suspended))
			if not current_user.confirmed:
				g.confirm_account = "Please access your email and confirm your account. \
				Or request a new confirmation link from your Profile"
				return func(*args, **kwargs)
			return func(*args, **kwargs)
		return func(*args, **kwargs)
	return decorated_function