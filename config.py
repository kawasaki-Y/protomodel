import os

class Config:
    # アプリケーションのルートディレクトリ
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # デバッグモード
    DEBUG = True
    
    # 秘密鍵
    SECRET_KEY = 'dev-secret-key'  # 本番環境では環境変数から読み込むこと
    
    # データベース設定 - SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 