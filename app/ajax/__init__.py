from flask import Blueprint
ajax = Blueprint('ajax', __name__)
from app.ajax import routes