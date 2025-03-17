import os
from datetime import timedelta

class Config:
    # アプリケーションのルートディレクトリ
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # デバッグモード
    DEBUG = True
    
    # 秘密鍵
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # データベース設定 - SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60) 