import re

from flask import Flask, current_app, flash, render_template, request, redirect, url_for, jsonify
from ..models import User, Post, SavedArticle, HeartedArticle, Tag, Category, Comment, load_user
from ..data_retrieval import latest_added_articles
from flask_login import login_required, current_user
from sqlalchemy import desc
from datetime import datetime
from app.article import article
from .. import db
from ..decorators import admin_required
from datetime import datetime
from ..forms import article_validator
from validator_collection import validators, checkers, errors



@article.route("/", methods=["GET", "POST"])
def articles():
    title = "Lang & Code - Articles"
    page = request.args.get('page', 1, type=int)
    if page:
        articles = Post.query.filter_by(published='publish').order_by(Post.pub_date.asc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
        if articles:
            return render_template("article/articles.html", 
                multiple_articles=articles.items, 
                pagination=articles,
                title=title)
        flash("The article you are looking for does not seem to exist.", "is-danger")
    latest_articles = latest_added_articles()
    return render_template("article/articles.html", multiple_articles=latest_articles, title=title)


@article.route("/<id>/show", methods=["GET", "POST"])
def show_articles(id):
    title = "Lang & Code - Show Articles"
    if id:
        article = Post.query.get(id)
        if article:
            return render_template("article/articles.html", article=article, title=article.title.title())
            flash("The article you are looking for does not seem to exist.", "is-danger")
    flash("The article with the id you requested was not found.")
    return redirect(url_for("article.articles"))


@article.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def add_article():
    title = "Lang & Code - New Article"
    current_url = "add_article"
    if current_user.is_admin():
        if request.method == "GET":
            return render_template("article/write_article.html", 
                title=title, 
                current_url=current_url)
        if request.method == "POST":
            article_title = request.form.get("articleTitle")
            article_body = request.form.get("articleBody")
            article_category = request.form.get("articleCategory")
            article_tags = request.form.get("articleTags")
            article_language_option = request.form.get("articleLanguageOption")
            article_publication_option = request.form.get("articlePublicationOption")
            validate = article_validator(article_title, 
                article_body, 
                article_category, 
                article_tags, 
                article_language_option, 
                article_publication_option)
            if not validate[0]:
                flash("Could not add to database. Some errors occured. Please review and try again later.", "is-warning")
                for e in validate[1]:
                    flash(e)
                return redirect(url_for("article.add_article"))
            article = Post(
                user_id=current_user.id, 
                title=article_title, 
                body=article_body, 
                category=article_category,
                tags_string=article_tags,
                language=article_language_option,
                published=article_publication_option)
            tags = [article.tags.append(add_tags(tag)) for tag in article_tags.split(",")]
            category = add_category(article_category)
            db.session.add(article)
            db.session.commit()
            if article:
                flash("Article added successfully!", "is-primary")
                return redirect(url_for('article.articles'))
            flash("Could not add to database. Might be an enternal error. Please try again later.", "is-warning")
            return render_template("article/write_article.html", title=title, current_url=current_url)
    flash("You do not have enough permission to write articles. Reserved for moderaters." , "is-danger")
    return redirect(url_for('article.articles'))


@article.route("/comment", methods=["GET", "POST"])
@login_required
def comment():
    title = "Lang & Code - Comment"
    if request.method == "POST":
        post_id = request.form.get("postId")
        comment_body = request.form.get("commentBody")
        if post_id and comment_body and checkers.is_string(comment_body) and len(comment_body) >= 10:
            article = Post.query.get(post_id)
            author = User.query.get(article.user_id)
            if article and author:
                comment = Comment(
                        user_id=current_user.id,
                        article_id=post_id,
                        body=comment_body,
                        approved=True)
                db.session.add(comment)
                db.session.commit()
                flash("Comment added successfully!", "is-primary")
                return redirect(url_for('article.show_articles', id=post_id))
            flash("Comment could not be added. Either post was not found or you cannot comment on it.", "is-primary")
            return redirect(url_for('article.articles'))
        flash("Some of your input data were not valid. Please check again and then submit.", "is-warning")
        flash("Comment must be a string of 10 characters at least.")
        return redirect(url_for('article.show_articles', id=post_id))
    flash("You do not have enough permission to comment on articles." , "is-warning")
    return redirect(url_for('article.show_articles', id=post_id))


def add_tags(tag):
    existing_tag = Tag.query.filter(Tag.name == tag.lower()).one_or_none()
    """if it does return existing tag objec to list"""
    if existing_tag is not None:
        return existing_tag
    else:
       new_tag = Tag()
       new_tag.name = tag.lower()
       return new_tag

def add_category(category):
    add_category = Category.query.filter(Category.name == category).one_or_none()
    """if it does return existing category objec to list"""
    if add_category is not None:
        pass
    else:
       new_category = Category(name=category)
       db.session.add(new_category)
       return new_category


@article.route("/<id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_article(id):
    title = "Lang & Code - Edit Article"
    current_url = "edit_article"
    if current_user.is_admin():
        article = Post.query.get(id)
        if request.method == "GET":
            if article:
                return render_template("article/edit_article.html", article=article, title=title, current_url=current_url)
            flash("The article you are trying to update does not exist.", "is-danger")
            return redirect(url_for('article.articles'))
        if request.method == "POST":
            article_title = request.form.get("articleTitle")
            article_body = request.form.get("articleBody")
            article_category = request.form.get("articleCategory")
            article_tags = request.form.get("articleTags")
            article_language_option = request.form.get("articleLanguageOption")
            article_publication_option = request.form.get("articlePublicationOption")
            validate = article_validator(article_title, 
                article_body, 
                article_category, 
                article_tags, 
                article_language_option, 
                article_publication_option)
            if not validate[0]:
                flash("Could not add to database. Some errors occured. Please review and try again later.", "is-warning")
                for e in validate[1]:
                    flash(e)
                return redirect(url_for("article.edit_article", id=id))
            update_article = Post.query.filter_by(
            id=id).update({
            Post.title:article_title, 
            Post.body:article_body, 
            Post.category:article_category, 
            Post.tags_string:article_tags,
            Post.language:article_language_option, 
            Post.published:article_publication_option})
            tags = [article.tags.append(add_tags(tag)) for tag in article_tags.split(",")]
            category = add_category(article_category)
            db.session.commit()
            if update_article:
                flash("Article updated successfully!", "is-primary")
                return redirect(url_for('article.show_articles', id=id))
            flash("Article could not be updated. You may not have permission to do so.")
            return redirect(url_for('article.articles', article=update_article))
    flash("You do not have enough permission to update articles. Reserved for moderaters." , "is-danger")
    return redirect(url_for('article.articles'))


@article.route("/<id>/delete", methods=["GET", "POST"])
@login_required
def delete_article(id):
    title = "Lang & Code - Delete Article"
    if current_user.is_admin() and request.method == "GET":
        article = Post.query.get(id)
        if article:
            db.session.delete(article)
            db.session.commit()
            flash('Article deleted successfully')
            return redirect(url_for('article.articles'))
        flash("The article you are trying to delete does not exist.", "is-danger")
        return redirect(url_for('article.articles'))
    flash("You do not have enough permission to delete articles. Reserved for admins." , "is-danger")
    return redirect(url_for('article.articles'))


@article.route("/comment/<id>/delete", methods=["GET", "POST"])
@login_required
def delete_comment(id):
    title = "Lang & Code - Delete Article"
    if request.method == "GET":
        comment = Comment.query.get(id)
        if comment:
            if current_user == comment.author or current_user.is_admin():
                db.session.delete(comment)
                db.session.commit()
                flash('Comment deleted successfully')
                return redirect(url_for('article.show_articles', id=comment.article_id))
            flash("You do not have permission to delete this comment.", "is-danger")
            return redirect(url_for('article.show_articles', id=comment.article_id))
        flash("The comment you are trying to delete does not exist.", "is-danger")
        return redirect(url_for('article.articles'))
    flash("You do not have enough permission to delete this comment." , "is-danger")
    return redirect(url_for('article.articles'))


@article.route("/save", methods=["GET", "POST"])
@login_required
def save_article():
    # 0 = unsaved, 1 = saved, 2 = already saved,
    # 3 = article does not exist, 4 = error
    if request.method == "GET":
        article_id = request.args.get("article_id")
        if article_id:
            check_article = Post.query.get(article_id)
            if check_article:
                check_saved = SavedArticle.query.filter_by(user_id=current_user.id, article_id=article_id).first()
                if check_saved:
                    return jsonify(message=2)
                else:
                    save_article = SavedArticle(state=0, user_id=current_user.id, article_id=article_id)
                    db.session.add(save_article)
                    db.session.commit()
                    if save_article:
                        return jsonify(message=1)
            return jsonify(message=3)
        return jsonify(message=4)


@article.route("/heart", methods=["GET", "POST"])
@login_required
def heart_article():
    # 0 = unsaved, 1 = hearted, 2 = already hearted,
    # 3 = article does not exist, 4 = error
    if request.method == "GET":
        article_id = request.args.get("article_id")
        if article_id:
            check_article = Post.query.get(article_id)
            if check_article:
                check_hearted = HeartedArticle.query.filter_by(user_id=current_user.id, article_id=article_id).first()
                if check_hearted:
                    return jsonify(message=2)
                else:
                    heart_article = HeartedArticle(user_id=current_user.id, article_id=article_id)
                    db.session.add(heart_article)
                    db.session.commit()
                    return jsonify(message=1)
            return jsonify(message=3)
        return jsonify(message=4)


@article.route("/tag/<tag>", methods=["GET", "POST"])
def tag(tag):
    title = "Lang & Code - Tags"
    page = request.args.get('page', 1, type=int)
    if request.method == "GET" and tag:
        articles = Post.query.join(Post.tags).filter(Tag.name==tag).order_by(Post.pub_date.asc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
        if articles:
            return render_template("article/tagged_articles.html", 
                multiple_articles=articles.items, 
                pagination=articles,
                tag=tag,
                title=title)
        flash("No results for tag '{}'.".format(tag))
        return redirect(url_for("article.articles"))
    return redirect(url_for("article.articles"))



@article.route("/category/<category>", methods=["GET", "POST"])
def category(category):
    title = "Lang & Code - Categories"
    page = request.args.get('page', 1, type=int)
    if request.method == "GET" and category:
        articles = Post.query.filter_by(published="publish",category=category).order_by(Post.pub_date.asc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
        if articles:
            return render_template("article/categories.html", 
                multiple_articles=articles.items, 
                pagination=articles,
                category=category,
                title=title)
        flash("No results for category '{}'.".format(category))
        return redirect(url_for("article.articles"))
    return redirect(url_for("article.articles"))
