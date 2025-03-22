import os
from datetime import timedelta

class Config:
    # アプリケーションのルートディレクトリ
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # デバッグモード
    DEBUG = True
    
    # データベース設定
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # セッション設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 静的ファイルのキャッシュ期間を1年に設定
    TEMPLATES_AUTO_RELOAD = False  # 本番環境ではテンプレートの自動リロードを無効化 