"""Flask config class."""
import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	"""Set Flask configuration vars."""

	# General Config
	TESTING = os.environ.get('TESTING') or False
	DEBUG = os.environ.get('DEBUG') or False
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SUPPRESS_SEND = False
	POSTS_PER_PAGE = 1
	SAVED_ARTICLES_PER_PAGE = 10
	USERS_PER_PAGE = 10
	MY_ARTICLES_PER_PAGE = 10
	FOLLOWING_PER_PAGE = 20
	FOLLOWERS_PER_PAGE = 20
	LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
	SESSION_PROTECTION = 'basic'
	SECRET_KEY = os.environ.get('SECRET_KEY') or b'your_secrete_key'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'db/app.db')
	MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
	MAIL_PORT = os.environ.get('MAIL_PORT') or 587
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = ['admin@dev.com']
	ADMINS_EMAILS_WHITELIST = os.environ.get('ADMINS_EMAILS_WHITELIST') or ADMINS
	MASTER_PASSWORD = os.environ.get('MASTER_PASSWORD')

class Development(Config):

	TESTING = os.environ.get('TESTING') or False
	DEBUG = os.environ.get('DEBUG') or True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SUPPRESS_SEND = False
	STEMMER_MAX_DATA_LEN = 500
	PARSER_MAX_DATA_LEN = 500 
	LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
	SESSION_PROTECTION = 'basic'
	SECRET_KEY = os.environ.get('SECRET_KEY') or b'your_secrete_key'
	SQLALCHEMY_DATABASE_URI = "postgresql://postgres@localhost/langandcodedbold" or 'sqlite:///' + os.path.join(basedir, 'db/app.db')
	MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
	MAIL_PORT = os.environ.get('MAIL_PORT') or 587
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'admin@dev.com'
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	MASTER_PASSWORD = os.environ.get('MASTER_PASSWORD') or 'password123'