from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from app.api import api
from ..exceptions import ValidationError


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    return error_response(400, message)

def unauthorized(message):
    return error_response(401, message)


def enternal_server_error(message):
    return error_response(500, message)


def method_not_allowed(message):
    return error_response(405, message)


@api.errorhandler(ValidationError)
def validation_error(e):
	return bad_request(e.args[0])