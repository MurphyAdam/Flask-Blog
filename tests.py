#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Post,\
HeartedArticle, SavedArticle, Comment, SuspenedUser, DeletedAccount
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@localhost/"

class UserModelCase(unittest.TestCase):


    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().followed.username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().follower.username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_users(self):
        # create four users
        DOMAIN = "@app.com"
        EMAILS = ["elm.majdi", "adamclark", "lana", "hopper", "greeg", "eleven", "someuser", "otheruser"]
        NAMES = ["Majdi Adam", "Adam Clark", "Lana Leonhart", "Hopper James", "Jane Hopper", "Some User", "Other User"]
        USERNAMES = ["Adamxk", "Clark57z", "LeonhartX77", "James478", "HopperX", "UserX", "OtherUser"]
        PASSWORD = "globalpass"
        for email, name, username in zip(EMAILS, NAMES, USERNAMES):
            email = email+DOMAIN
            add_user = User(fullname=name, username=username, email=email, account_state=0)
            add_user.set_password(PASSWORD)
            db.session.add(add_user)
            db.session.commit()
        users = []
        index = 0
        for user in User.query.all():
            users.append(user)
        for user in users:
            user.follow(users[index])
            index += 1
        db.session.commit()


    def test_creating_posts(self):
        for user in User.query.all():
            new_post = Post(title="Test post", body="post from User", user_id=user.id)
            db.session.add(new_post)
        db.session.commit()


    def test_adding_comments(self):
        for post in Post.query.all():
            comment = Comment(
                user_id=self.id,
                article_id=post.id,
                body="Just testing adding comments",
                approved=True)
            db.session.add(comment)
        db.session.commit()


    def test_deleting_comments(self):
        for comment in Comment.query.all():
            print("deleting", comment)
            db.session.delete(comment)
        db.session.commit()


    def test_deleting_posts(self):
        for post in Post.query.all():
            print("deleting", post)
            db.session.delete(post)
        db.session.commit()


    def test_suspending_users(self):
        for user in User.query.all():
            user.account_state == 0
        db.session.commit()


    def test_deleting_users(self):
        for user in User.query.all():
            deleted_account = DeletedAccount(email=self.email, reason="Stuff")
            db.session.add(deleted_account)
            db.session.delete(self)
        db.session.commit()


if __name__ == '__main__':
    unittest.main(verbosity=2)
