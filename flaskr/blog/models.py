import datetime
import uuid

from sqlalchemy.ext.hybrid import hybrid_property

from flask import url_for

from flaskr import db, create_hash
from flaskr.auth.models import User, HubUser


def generate_post_id(self):
    """Generate a new UUID for use as the `post_id`"""
    return uuid.uuid4()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.ForeignKey(User.id), nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)

    # User object backed by author_id
    # lazy="joined" means the user is returned with the post in one query
    author = db.relationship(User, lazy="joined", backref="posts")

    @property
    def update_url(self):
        return url_for("blog.update", id=self.id)

    @property
    def delete_url(self):
        return url_for("blog.delete", id=self.id)


class HubPost(db.Model):
    __tablename__ = 'hub_post'
    _post_hash_key = db.Column(
        "post_hash_key", db.String(64), primary_key=True)
    created = db.Column(
        db.DateTime, nullable=False, index=True,
        default=datetime.datetime.utcnow(),
    )
    post_id = db.Column(
        db.String, nullable=False, index=True, unique=True, default=generate_post_id
    )

    author = db.relationship(
        'hub_user', secondary='link_author', backref='hub_post'
    )

    @hybrid_property
    def post_hash_key(self):
        """return the post hash key"""
        return self._post_hash_key

    @post_hash_key.setter
    def post_hash_key(self, post_id):
        """hash the `post_id` and save the result"""
        new_hash_key = create_hash(post_id)
        self._post_hash_key = new_hash_key


class LinkAuthor(db.Model):
    __tablename__ = 'link_author'
    _author_hash_key = db.Column(
        "author_hash_key", db.String(64), primary_key=True
    )
    created = db.Column(
        db.DateTime, nullable=False, index=True,
        default=datetime.datetime.utcnow(),
    )
    post_hash_key = db.Column(
        db.ForeignKey(HubPost.post_hash_key), nullable=False
    )
    user_hash_key = db.Column(
        db.ForeignKey(HubUser.user_hash_key), nullable=False
    )

    @hybrid_property
    def author_hash_key(self):
        """Return the author hash key"""
        return self._author_hash_key

    @author_hash_key.setter
    def author_hash_key(self, post_hash_key, user_hash_key):
        """create a hash key and save it"""
        new_hash_key = create_hash(post_hash_key, user_hash_key)
        self._author_hash_key = new_hash_key


class SatPostContent(db.Model):
    __tablename__ = 'sat_post_content'
    post_hash_key = db.Column(
        db.ForeignKey(HubPost.post_hash_key), nullable=False, primary_key=True
    )
    created = db.Column(
        db.DateTime, nullable=False, primary_key=True,
        default=datetime.datetime.utcnow(),
    )
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
