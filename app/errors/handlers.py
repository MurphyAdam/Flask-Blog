from flask import make_response, render_template, flash, request, jsonify
from app.errors import errors
from app.api.errors import error_response as api_error_response
from .. import db



##########################  HTTP ERRORS ###########################

title = "Lang&Code - HTTP CODE ERROR"
 



def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']


@errors.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(404)
def page_not_found(e):
    if wants_json_response():
        return api_error_response(404)
    else:
        title = "Lang&Code - Not Found"
        flash("Not Found or Under Construction: The page you are trying to view does not seem to exist." , "is-warning")
        return render_template("errors/not-found.html", title=title), 404


@errors.app_errorhandler(405)
def method_not_allowed(e):
    if wants_json_response():
        return api_error_response(405)
    title = "Method Not Allowed"
    flash("The issued method is not allowed with this endpoint.")
    return render_template("errors/not-found.html", title=title), 405


@errors.app_errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    title = "Lang&Code - Internal Server Error occured."
    flash("Internal Server Error: The server has been fed invalid data or is undergoing maintance." , "is-danger")
    return render_template("errors/not-found.html", title=title), 500

@errors.app_errorhandler(403)
def forbidden(e):
    if wants_json_response():
        return api_error_response(403)
    title = "Lang&Code - Forbidden"
    flash("Forbidden to access this page. Needs advanced permissions." , "is-danger")
    return render_template("errors/not-found.html", title=title), 403


@errors.app_errorhandler(400)
def bad_request(e):
    if wants_json_response():
        return api_error_response(500)
    title = "Lang&Code - Bad Request"
    flash("Bad Request" , "is-danger")
    return render_template("errors/not-found.html", title=title), 400


@errors.app_errorhandler(401)
def unauthorized(e):
    if wants_json_response():
        return api_error_response(401)
    title = "Lang&Code - Unauthorized"
    flash("Unauthorized: You do not have enough permission to access this page. Please login with proper credentials." , "is-danger")
    return render_template("errors/not-found.html", title=title), 401
