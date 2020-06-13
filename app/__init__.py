import logging, os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_seasurf import SeaSurf
from config import Config, Development


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
moment = Moment()
mail = Mail()
seasurf = SeaSurf()

login_manager.refresh_view = "main.index"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate (logout and re-login) to access this page.")
login_manager.needs_refresh_message_category = "is-info"


def create_app(config_class=Development):
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)

    # Application Configuration
    app.config.from_object(config_class)
    with app.app_context():
        # Initialize Plugins
        login_manager.init_app(app)
        db.init_app(app)
        mail.init_app(app)
        moment.init_app(app)
        migrate.init_app(app, db)
        seasurf.init_app(app)
        # Initialize Global db
        db.create_all()
        # Register Blueprints
        # MAIN BP
        from app.main import main as main_blueprint
        app.register_blueprint(main_blueprint)
        # AUTH BP
        from app.auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        # ADMIN BP
        from app.admin import admin as admin_blueprint
        app.register_blueprint(admin_blueprint, url_prefix='/admin')
        # USER BP
        from app.user import user as user_blueprint
        app.register_blueprint(user_blueprint, url_prefix='/user')
        # ARTICLE BP
        from app.article import article as article_blueprint
        app.register_blueprint(article_blueprint, url_prefix='/articles')
        # AJAX BP
        from app.ajax import ajax as ajax_blueprint
        app.register_blueprint(ajax_blueprint, url_prefix='/ajax')
        # API BP
        from app.api import api as api_blueprint
        app.register_blueprint(api_blueprint, url_prefix='/api')
        # ERRORS BP
        from app.errors import errors as errors_blueprint
        app.register_blueprint(errors_blueprint)
        # Configute Debugging
        if app.debug or app.testing:
        # ...
            if app.config['MAIL_SERVER']:
                auth = None
                if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                    auth = (app.config['MAIL_USERNAME'],
                            app.config['MAIL_PASSWORD'])
                secure = None
                if app.config['MAIL_USE_TLS']:
                    secure = ()
                mail_handler = SMTPHandler(
                    mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                    fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                    toaddrs=app.config['ADMINS'], subject='LangandCode Failure',
                    credentials=auth, secure=secure)
                mail_handler.setLevel(logging.ERROR)
                app.logger.addHandler(mail_handler)

            if app.config['LOG_TO_STDOUT']:
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(logging.INFO)
                app.logger.addHandler(stream_handler)
            else:
                if not os.path.exists('logs'):
                    os.mkdir('logs')
                file_handler = RotatingFileHandler('logs/applog.log',
                                                   maxBytes=20480, backupCount=20)
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s '
                    '[in %(pathname)s:%(lineno)d]'))
                file_handler.setLevel(logging.INFO)
                app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('App startup')
        return app
