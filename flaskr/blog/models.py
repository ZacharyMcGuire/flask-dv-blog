import datetime

from flaskr import db
from flaskr.auth.models import HubUser


class HubPost(db.Model):
    __tablename__ = 'hub_post'
    post_hash_key = db.Column(db.String(64), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, index=True, default=datetime.datetime.utcnow())
    post_id = db.Column(db.String, nullable=False, index=True, unique=True)

    author = db.relationship(HubUser, secondary='link_author', backref='hub_post', uselist=False)
    post_content = db.relationship('SatPostContent', backref='hub_post', uselist=False,
                                   primaryjoin="and_(HubPost.post_hash_key==SatPostContent.post_hash_key, "
                                               f"SatPostContent.record_end > '{datetime.datetime.utcnow()}')")
    effectivity = db.relationship('SatPostEffectivity', backref='hub_post', uselist=False,
                                  primaryjoin="and_(HubPost.post_hash_key==SatPostEffectivity.post_hash_key, "
                                              f"SatPostEffectivity.record_end > '{datetime.datetime.utcnow()}')")

    __mapper_args__ = {
        "order_by": created.desc()
    }


class LinkAuthor(db.Model):
    __tablename__ = 'link_author'
    author_hash_key = db.Column("author_hash_key", db.String(64), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, index=True, default=datetime.datetime.utcnow())
    post_hash_key = db.Column(db.ForeignKey(HubPost.post_hash_key), nullable=False)
    user_hash_key = db.Column(db.ForeignKey(HubUser.user_hash_key), nullable=False)

    __mapper_args__ = {
        "order_by": created.desc()
    }


class SatPostContent(db.Model):
    __tablename__ = 'sat_post_content'
    post_hash_key = db.Column(db.ForeignKey(HubPost.post_hash_key), nullable=False, primary_key=True)
    record_start = db.Column(db.DateTime, nullable=False, primary_key=True, default=datetime.datetime.utcnow)
    record_end = db.Column(db.DateTime, nullable=False, index=True, server_default='9999-12-31 00:00:00.000000')
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)

    __mapper_args__ = {
        "order_by": record_start.desc()
    }


class SatPostEffectivity(db.Model):
    __tablename__ = 'sat_post_effectivity'
    post_hash_key = db.Column(db.ForeignKey(HubPost.post_hash_key), nullable=False, primary_key=True)
    record_start = db.Column(db.DateTime, nullable=False, primary_key=True, default=datetime.datetime.utcnow)
    record_end = db.Column(db.DateTime, nullable=False, index=True, server_default='9999-12-31 00:00:00.000000')
    post_status = db.Column(db.String(32), nullable=False, default="Active")

    __mapper_args__ = {
        "order_by": record_start.desc()
    }
