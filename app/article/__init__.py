from flask import Blueprint
article = Blueprint('article', __name__)
from app.article import routes
