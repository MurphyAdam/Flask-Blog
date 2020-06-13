from flask import current_app, jsonify, g, abort, request, render_template
from flask_login import login_required, current_user
from ..decorators import admin_required
from ..models import User, Post,\
Tag, Category
from app.ajax import ajax
from .. import db
from ..forms import article_validator



@ajax.route("articles/<id>/show", methods=["GET"])
def show_articles(id):
    if id:
        article = Post.query.get(id)
        if article:
            return jsonify(
                {
                "message":"Article retrieved", 
                "success": True,
                "category":"is-primary",
                "article":article.to_dict(all=True)}), 200
        return jsonify(
            {
            "message":"Article not found", 
            "success": False,
            "category":"is-warning"}), 404
    return jsonify(
                {
                "message":"Id required to retrieve the article", 
                "success": False,
                "category":"is-warning"}), 304


@ajax.route("articles/new", methods=["GET", "POST"])
@login_required
@admin_required
def add_article():
    title = "Lang & Code - New Article"
    if request.method == "GET":
        return render_template(
            "vue/article/make.html", 
            title=title)
    if request.method == "POST":
        json_data = request.get_json()
        article_title = json_data.get("title")
        article_body = json_data.get("body")
        article_category = json_data.get("category")
        article_tags = json_data.get("tags")
        article_language_option = json_data.get("language")
        article_publication_option = json_data.get("publication")
        validate = article_validator(article_title, 
            article_body, 
            article_category, 
            article_tags, 
            article_language_option, 
            article_publication_option)
        if not validate[0]:
            for e in validate[1]:
                return jsonify({
            	"message":e, 
            	"success": False,
            	"category":"is-info"})
        article = Post(
            user_id=current_user.id, 
            title=article_title, 
            body=article_body, 
            category=article_category,
            tags_string=article_tags,
            language=article_language_option,
            published=article_publication_option)
        tags = [article.tags.append(add_tags(tag.strip())) for tag in article_tags.split(",")]
        category = add_category(article_category)
        db.session.add(article)
        db.session.commit()
        if article:
            return jsonify(
                {
                "message":"Article added successfully!", 
                "success": True,
                "category":"is-primary",
                "article":article.to_dict()})
        return jsonify({
            "message":"Could not add to database. Might be an enternal error. Please try again later.", 
            "success": False,
            "category":"is-warning"})


@ajax.route("articles/<id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_article(id):
    title = "Lang & Code - Edit Article"
    current_url = "edit_article"
    article = Post.query.get(id)
    if request.method == "GET":
        if article:
            return render_template(
                "article/edit_article.html", 
                article=article, 
                title=title, 
                current_url=current_url)
        flash("The article you are trying to update does not exist.", "is-danger")
        return redirect(url_for('article.articles'))
    if request.method == "POST":
        json_data = request.get_json()
        article_title = json_data.get("articleTitle")
        article_body = json_data.get("articleBody")
        article_category = json_data.get("articleCategory")
        article_tags = json_data.get("articleTags")
        article_language_option = json_data.get("articleLanguageOption")
        article_publication_option = json_data.get("articlePublicationOption")
        validate = article_validator(
            article_title, 
            article_body, 
            article_category, 
            article_tags, 
            article_language_option, 
            article_publication_option)
        if not validate[0]:
            for e in validate[1]:
                return jsonify({
                "message":e, 
                "success": False,
                "category":"is-info"})
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
            return jsonify(
                {
                "message":"Article updated successfully!", 
                "success": True,
                "category":"is-primary",
                "article":article.to_dict()})
        return jsonify({
            "message":"Could not add to database. Might be an enternal error."
            " Or that you may not have permission to do so. Please try again later.", 
            "success": False,
            "category":"is-warning"})


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
