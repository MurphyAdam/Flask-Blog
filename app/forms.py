import re

from flask import flash
from flask_login import current_user
from validator_collection import validators, checkers, errors

from .models import User



def is_valid_password(password):
    if password and checkers.is_string(password) and len(password) >= 8 and not password.isspace():
        return True
    return False


def is_valid_username(username):
    pattern = r'^[A-Za-z0-9_]*$'
    valid = re.search(pattern, username)
    if username and len(username) >= 4 and valid and not username.isspace():
        return True
    else:
        return False

def is_valid_fullname(fullname):
    pattern = r'^[A-Za-z\s+]*$'
    valid = re.search(pattern, fullname)
    if fullname and len(fullname) >= 3 and valid and not fullname.isspace():
        return True
    else:
        return False

def signin_validator(email, password):
    errors = []
    if email and checkers.is_email(email):
        user_to_login = User.query.filter_by(email=email).first()
        if user_to_login:
            if user_to_login.check_password(password):
                pass
            else:
                errors.append("Password is incorrect.")
        else:
            errors.append("No account with this email exists.")
    else:
        errors.append("Email or password is invalid")
    if len(errors) == 0:
        return True, errors, user_to_login
    if len(errors) > 0:
        return False, errors, None


def reset_password_validator(token, password, confirm_password):
    errors = []
    if token and checkers.is_string(token):
        pass
    else:
        errors.append("Token is invalid. Request a fresh one.")
    if password and is_valid_password(password):
        if confirm_password is not None and password == confirm_password:
            pass
        else:
            errors.append("Passwords do not match")
    else:
        errors.append("Password is invalid: must be 8 characters minimum and a mixture of both letters and numbers.")
    if len(errors) == 0:
        return True, errors
    if len(errors) > 0:
        return False, errors



def update_password_validator(current_password, new_password, confirm_new_password):
    errors = []
    if current_password and current_user:
        check_current_password = current_user.check_password(current_password)
        if check_current_password:
            pass
        else:
            errors.append("Current password is not correct.")
    else:
        errors.append("Current password is invalid.")
    if new_password and is_valid_password(new_password):
        if confirm_new_password is not None and new_password == confirm_new_password:
            pass
        else:
            errors.append("Passwords do not match")
    else:
        errors.append("Password is invalid: must be 8 characters minimum and a mixture of both letters and numbers.")
    if len(errors) == 0:
        return True, errors
    if len(errors) > 0:
        return False, errors


def signup_validator(fullname, username, email, password, password2):
    errors = []
    if email and checkers.is_email(email):
        check_email = User.query.filter_by(email=email).first()
        if not check_email:
            pass
        else:
            errors.append("An account is already registred with this email.")
    else:
        errors.append("Email is invalid.")
    if password and is_valid_password(password):
        if password2 is not None and password == password2:
            pass
        else:
            errors.append("Passwords do not match")
    else:
        errors.append("Password is invalid: must be 8 characters minimum and a mixture of both letters and numbers.")
    if fullname and checkers.is_string(fullname) and is_valid_fullname(fullname):
        pass
    else:
        errors.append("Fullname is invalid: must be three characters minimum and cannot have any special characters.")
    if username and checkers.is_string(username) and is_valid_username(username):
        check_username = User.query.filter_by(username=username).first()
        if not check_username:
            pass
        else:
            errors.append("This username is already taken. Please try another.") 
    else:
        errors.append("Username is invalid. Usernames must be 4 characters minimum and must have only letters, numbers, and/ or underscores")
    if len(errors) == 0:
        return True, errors
    if len(errors) > 0:
        return False, errors


def reset_password_validator(token, password, confirm_password):
    errors = []
    if token and checkers.is_string(token):
        pass
    else:
        errors.append("Token is invalid. Request a fresh one.")
    if password and is_valid_password(password):
        if confirm_password is not None and password == confirm_password:
            pass
        else:
            errors.append("Passwords do not match")
    else:
        errors.append("Password is invalid: must be 8 characters minimum and a mixture of both letters and numbers.")
    if len(errors) == 0:
        return True, errors
    if len(errors) > 0:
        return False, errors


def article_validator(article_title, 
    article_body, 
    article_category, 
    article_tags, 
    article_language_option, 
    article_publication_option):
    errors = []
    if article_title and checkers.is_string(article_title) and len(article_title) >= 10 and not article_title.isspace():
        pass
    else:
        errors.append("Title is invalid. Must be a string of 10 characters at least.")
    if article_body and checkers.is_string(article_body) and len(article_body) >= 250 and not article_body.isspace():
        pass
    else:
        errors.append("Article Body is invalid: must be 250 characters minimum.")
    if article_category and checkers.is_string(article_category) and len(article_category) >= 3 and not article_category.isspace():
        pass
    else:
        errors.append("Category is invalid. Must be three characters minimum.")
    if article_tags and checkers.is_string(article_tags) and len(article_tags) >= 3 and not article_tags.isspace():
        pass
    else:
        errors.append("Tags is invalid. Must be at least one tag of three characters minimum.")
    if article_language_option and checkers.is_string(article_language_option) and not article_language_option.isspace():
        pass
    else:
        errors.append("Article language is invalid. Choose language.")
    if article_publication_option and checkers.is_string(article_publication_option) and not article_publication_option.isspace():
        pass
    else:
        errors.append("Publication option is invalid. Choose Publication option.")
    if len(errors) == 0:
        return True, errors
    if len(errors) > 0:
        return False, errors
