import os
from datetime import timedelta

class Config:
    # アプリケーションのルートディレクトリ
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # デバッグモード
    DEBUG = True
    
    # 秘密鍵
    SECRET_KEY = 'your-secret-key'
    
    # データベース設定 - SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 静的ファイルのキャッシュ期間を1年に設定
    TEMPLATES_AUTO_RELOAD = False  # 本番環境ではテンプレートの自動リロードを無効化 