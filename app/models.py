from flask_login import UserMixin
from werkzeug.security import check_password_hash
from app import db

class User(UserMixin, db.Model):
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first() 