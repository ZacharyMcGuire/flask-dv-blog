import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr import db, create_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column("password", db.String, nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """Store the password as a hash for security."""
        self._password = generate_password_hash(value)

    def check_password(self, value):
        return check_password_hash(self.password, value)


class HubUser(db.Model):
    __tablename__ = 'hub_user'
    _user_hash_key = db.Column(
        "user_hash_key", db.String(64), primary_key=True)
    created = db.Column(
        db.DateTime, nullable=False, index=True,
        default=datetime.datetime.utcnow(),
    )
    user_id = db.Column(db.Integer, nullable=False, index=True, unique=True)

    @hybrid_property
    def user_hash_key(self):
        """return the user hash key"""
        return self._user_hash_key

    @user_hash_key.setter
    def user_hash_key(self, user_id):
        """hash the `user_id` and save the result"""
        new_hash_key = create_hash(user_id)
        self._user_hash_key = new_hash_key


class SatUserInfo(db.Model):
    __tablename__ = 'sat_user_info'
    user_hash_key = db.Column(
        db.ForeignKey(HubUser.user_hash_key), nullable=False, primary_key=True
    )
    created = db.Column(
        db.DateTime, nullable=False, primary_key=True,
        default=datetime.datetime.utcnow(),
    )
    username = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column("password", db.String, nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """Store the password as a hash for security."""
        self._password = generate_password_hash(value)

    def check_password(self, value):
        return check_password_hash(self.password, value)
