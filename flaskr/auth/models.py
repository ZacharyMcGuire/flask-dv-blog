import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash

from flaskr import db


class HubUser(db.Model):
    __tablename__ = 'hub_user'
    user_hash_key = db.Column("user_hash_key", db.String(64), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, index=True, default=datetime.datetime.utcnow)
    username = db.Column(db.String, unique=True, nullable=False)
    auth = db.relationship('SatUserAuth', backref='hub_user', uselist=False,
                           primaryjoin="and_(HubUser.user_hash_key==SatUserAuth.user_hash_key, "
                           f"SatUserAuth.record_end > '{datetime.datetime.utcnow()}')")


class SatUserAuth(db.Model):
    __tablename__ = 'sat_user_auth'
    user_hash_key = db.Column(db.String(64), db.ForeignKey(HubUser.user_hash_key), nullable=False, primary_key=True)
    record_start = db.Column(db.DateTime, nullable=False, primary_key=True, default=datetime.datetime.utcnow)
    record_end = db.Column(db.DateTime, nullable=False, index=True, server_default='9999-12-31 00:00:00.000000')
    _password = db.Column("password", db.String, nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """Store the password as a hash for security."""
        self._password = generate_password_hash(value)
