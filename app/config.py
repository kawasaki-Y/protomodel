import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # セッション設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # セッションの有効期間
    SESSION_TYPE = 'filesystem'  # または 'redis' などの他のバックエンド
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False  # 本番環境ではTrueに設定
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # データベース設定
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # その他の設定
    # ... 