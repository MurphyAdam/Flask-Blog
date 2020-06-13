from flask_login import current_user
from .models import db, Post, SavedArticle
from sqlalchemy import desc


def latest_added_articles(n):
    articles = Post.query.filter_by(published='publish').order_by(desc(Post.pub_date)).limit(n).all()
    if articles:
        return articles
    return None

def latest_saved_articles(n):
    saved_articles = SavedArticle.query.filter_by(user_id=current_user.id).order_by(desc(SavedArticle.date_saved)).limit(n).all()
    if saved_articles:
        return saved_articles
    return None
