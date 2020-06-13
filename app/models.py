# -*- coding: utf-8 -*-

import os
import jwt
import json
import base64

from datetime import datetime, timedelta
from time import time
from hashlib import md5

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import Flask, url_for
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc, distinct
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager



@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


class Follow(db.Model):
    __tablename__ = 'follows'
    __table_args__ = {'extend_existing': True}
    follower_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    state = db.Column(db.Integer, default=0)
    date_followed = db.Column(db.DateTime, default=datetime.utcnow)


class ReportedUser(db.Model):
    __tablename__ = 'reported_users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    reported_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    subject = db.Column(db.String)
    body = db.Column(db.Text)
    handled = db.Column(db.Boolean)
    action_taken = db.Column(db.String)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Suspended User %r>' % self.user_id


class User(UserMixin, db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column('user_id',db.Integer , primary_key=True)
    fullname = db.Column('fullname', db.String(), unique=False , index=True)
    username = db.Column('username', db.String(), unique=False , index=True)
    password = db.Column('password' , db.String())
    email = db.Column('email',db.String(),unique=True , index=True)
    role = db.Column('role', db.Integer(), default=0)
    confirmed = db.Column('confirmed', db.Boolean, default=False)
    account_state = db.Column('account_state', db.Integer(), default=1)
    about_me = db.Column('about_me' , db.String())
    last_seen = db.Column('last_seen' , db.DateTime(timezone=True), default=datetime.utcnow)
    registered_on = db.Column('registered_on' , db.DateTime(timezone=True), server_default=func.now())
    last_message_read_time = db.Column('last_message_read_time', db.DateTime)
    token = db.Column('token', db.String(), index=True, unique=True)
    token_expiration = db.Column('token_expiration', db.DateTime)
    suspension = db.relationship('SuspenedUser', backref='suspended_user', lazy='dynamic', cascade="all, delete-orphan")
    saved_articles = db.relationship('SavedArticle', backref='saved_post', lazy='dynamic', cascade="all, delete-orphan")
    hearted_articles = db.relationship('HeartedArticle', backref='hearted_post', lazy='dynamic', cascade="all, delete-orphan")
    articles = db.relationship('Post', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    contact_us_messages = db.relationship('ContactUs', backref='user',lazy='dynamic', cascade="all, delete-orphan")

    followed = db.relationship('Follow', 
        foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), 
        lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], 
        backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

    reported = db.relationship('ReportedUser', foreign_keys=[ReportedUser.reporter_id], 
        backref=db.backref('reporter', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    reporters = db.relationship('ReportedUser', 
        foreign_keys=[ReportedUser.reported_id], backref=db.backref('reported', lazy='joined'), 
        lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email in current_app.config['ADMINS_EMAILS_WHITELIST']:
            self.role = 1
            # To have your admin account confirmed automatically, 
            # set self.confirmed to True, recommended only for development
            self.confirmed = False


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def check_master_password(self, password):
        master_password = current_app.config['MASTER_PASSWORD']
        master_password_hash = generate_password_hash(password)
        return check_password_hash(master_password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def report(self, user, subject, body):
        r = ReportedUser(reporter=self, 
            reported=user, 
            subject=subject, 
            body=body, 
            handled=False, 
            action_taken=None)
        db.session.add(r)

    def is_reported(self):
        return self.reported.filter_by(reported_id=self.id).first() is not None

    def has_reported(self, user):
        return self.reported.filter_by(reporter_id=user.id).first() is not None


    def to_dict(self, include_email=False, basic=False):
        if basic:
            data = {
                'id': self.id,
                'username': self.username,
                'last_seen': self.last_seen.isoformat() + 'Z',
                'about_me': self.about_me,
                '_links': {
                    'avatar': self.avatar(128)
                }
            }
        else:
            data = {
                'id': self.id,
                'username': self.username,
                'last_seen': self.last_seen.isoformat() + 'Z',
                'about_me': self.about_me,
                'post_count': self.articles.count(),
                'follower_count': self.followers.count(),
                'followed_count': self.followed.count(),
                '_links': {
                    'avatar': self.avatar(128)
                }
            }
        if include_email:
            data['email'] = self.email
        return data

    def timestamp2date(self, timestamp):
        if timestamp:
            return datetime.fromtimestamp(timestamp)

    def date2timestamp(self, date):
        if date:
            return datetime.timestamp(date)

    def article_is_saved(self, article):
        return self.saved_articles.filter_by(article_id=article).count() > 0

    def article_is_hearted(self, article):
        return self.hearted_articles.filter_by(article_id=article).count() > 0


    def add_notification(self, name, body=None, category=None):
        n = Notification(name=name, body=body, seen=False, user=self, category=category if category else None)
        db.session.add(n)
        return n

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


    def get_api_token(self, expires_in=3600):
        return jwt.encode(
            {'token': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_api_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['token']
        except:
            return None
        return User.query.get(id)


    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def is_admin(self):
        if self.role == 1:
            return True
        return False

    def has_valid_account_state(self):
        if self.account_state == 1:
            return True
        return False

    def is_suspened(self):
        if self.account_state == 0:
            return True
        return False

    def has_god_powers(self):
        return False

    def __repr__(self):
        return '<User %r>' % (self.username)


class AnonymousUser(AnonymousUserMixin):

    def is_admin(self):
        return False


class SavedArticle(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.Integer)
    date_saved = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    article_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Saved article %r>' % self.article_id


class HeartedArticle(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    article_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    date_hearted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Hearted article %r>' % self.article_id


post_tag = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
    )

class Post(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    body = db.Column(db.Text)
    category = db.Column(db.String())
    language = db.Column(db.String())
    published = db.Column(db.String())
    pub_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    saved_articles = db.relationship('SavedArticle', backref='saved_articles', lazy='dynamic', cascade="all, delete-orphan")
    hearted_articles = db.relationship('HeartedArticle', backref='hearted_articles', lazy='dynamic', cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='comment_article', lazy='dynamic', cascade="all, delete-orphan")
    tags_string = db.Column(db.String())
    tags = db.relationship('Tag',secondary=post_tag, 
                        back_populates="posts", single_parent=True, cascade="all, delete-orphan")


    def to_dict(self, all=False):
        data = {
            'id' : self.id,
            'author' : User.query.get(self.user_id).to_dict(),
            'title': self.title,
            'body': self.body,
            'category': self.category,
            'tags': self.tags_string,
            'language':self.language,
            'published' : self.published,
            'date_created' : self.pub_date,
            'update_date' : self.update_date
        }
        if all:
            data["is_saved"] = User.query.get(self.user_id).article_is_saved(self.id)
            data["is_hearted"] = User.query.get(self.user_id).article_is_saved(self.id)
            data["has_comments"] = self.has_comments()
        return data


    def has_comments(self):
        return self.comments.filter_by(approved=True).count() > 0

    def __repr__(self):
        return '<Post %r>' % self.title


class Comment(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    article_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    approved = db.Column(db.Boolean(), default=True)
    date_commented = db.Column(db.DateTime(), default=datetime.utcnow, index=True)


class Tag(db.Model):
    __table_args__ = {'extend_existing': True}
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, unique=True, nullable=False)
    posts = db.relationship('Post', secondary = post_tag,
                            back_populates = "tags")

class Category(db.Model):
    __table_args__ = {'extend_existing': True}
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, unique=True)


class AboutUs(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String)
    company_description = db.Column(db.String)
    company_location = db.Column(db.String)
    company_email = db.Column(db.String)
    company_phone = db.Column(db.String)
    company_founder = db.Column(db.String)
    company_year_founded = db.Column(db.String)
    company_goals = db.Column(db.Text)
    company_history = db.Column(db.Text)
    company_editable_about_us = db.Column(db.Text)
    company_tou = db.Column(db.Text)
    company_privacy_policy = db.Column(db.Text)
    company_language = db.Column(db.String)
    company_api_docs = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<AboutUs %r>' % self.company_name


class ContactUs(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    is_user = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    fullname = db.Column(db.String)
    email = db.Column(db.String)
    subject = db.Column(db.String)
    body = db.Column(db.Text)
    seen = db.Column(db.Boolean)
    contact_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Is user %r>' % self.is_user


class SuspenedUser(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    note = db.Column(db.String)
    date_suspended = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Suspended User %r>' % self.user_id


class DeletedAccount(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    reason = db.Column(db.Text)
    date_deleted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Deleted Account %r>' % self.email
