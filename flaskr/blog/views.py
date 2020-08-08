import datetime
import uuid

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from sqlalchemy import text
from werkzeug.exceptions import abort

from flaskr import db, create_hash
from flaskr.auth.views import login_required
from flaskr.blog.models import HubPost, LinkAuthor, SatPostContent, SatPostEffectivity

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    posts = HubPost.query\
        .join(HubPost.post_content)\
        .join(HubPost.effectivity)\
        .join(HubPost.author)\
        .filter(text("sat_post_effectivity.post_status = 'Active'"))
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.
    Checks that the id exists and optionally that the current user is
    the author.
    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = HubPost.query.filter_by(post_id=id).first()
    if post is None:
        abort(404, f"Post id {id} does not exist.")

    if check_author and post.author.username != g.user.username:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            post_id = uuid.uuid4().__str__()
            post_hash_key = create_hash(post_id)
            user_hash_key = g.user.user_hash_key
            author_hash_key = create_hash(post_hash_key, user_hash_key)
            db.session.add(HubPost(post_hash_key=post_hash_key, post_id=post_id))
            db.session.add(LinkAuthor(
                author_hash_key=author_hash_key,
                post_hash_key=post_hash_key,
                user_hash_key=user_hash_key
            ))
            db.session.add(SatPostContent(post_hash_key=post_hash_key, title=title, body=body))
            db.session.add(SatPostEffectivity(post_hash_key=post_hash_key))
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            post.post_content.record_end = datetime.datetime.utcnow()
            db.session.add(SatPostContent(post_hash_key=post.post_hash_key, title=title, body=body))
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    post = get_post(id)
    post.effectivity.record_end = datetime.datetime.utcnow()
    db.session.add(SatPostEffectivity(post_hash_key=post.post_hash_key, post_status="Deleted"))
    db.session.commit()
    return redirect(url_for("blog.index"))
