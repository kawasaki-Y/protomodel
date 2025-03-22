from flask_login import UserMixin
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    """
    ユーザーモデル
    
    アプリケーションのユーザー情報を管理するモデル。
    認証・認可に必要な基本的な情報を保持する。
    """
    
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    # 基本情報
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップを完全修飾パスで定義
    revenue_businesses = db.relationship('app.models.business.RevenueBusiness', backref='user', lazy=True)

    # パスワードのハッシュ化と検証用メソッド
    def set_password(self, password):
        """
        パスワードをハッシュ化して保存
        
        Args:
            password (str): 生のパスワード
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        パスワードの検証
        
        Args:
            password (str): 検証するパスワード
            
        Returns:
            bool: パスワードが正しければTrue、そうでなければFalse
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """デバッグ用の文字列表現"""
        return f'<User {self.email}>' 