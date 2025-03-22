import os
from datetime import timedelta

class Config:
    # ベースディレクトリの設定
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # インスタンスディレクトリの設定
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    
    # データベースURIの設定
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(INSTANCE_DIR, "app.db")}'
    
    # その他の設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    @staticmethod
    def init_app(app):
        # インスタンスディレクトリの作成
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)

    # セッション設定
    SESSION_TYPE = 'filesystem'  # または 'redis' などの他のバックエンド
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False  # 本番環境ではTrueに設定
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # その他の設定
    # ... 