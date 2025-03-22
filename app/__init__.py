# アプリケーションパッケージの初期化
# このファイルはappディレクトリをPythonパッケージとして認識させるために必要です 

from flask import Flask
from .config import Config
from .extensions import db, init_extensions
from flask_login import current_user, LoginManager
import os
from .models.user import User
from .models.business import RevenueBusiness
from flask_migrate import Migrate

def format_number(value):
    """
    数値を3桁区切りでフォーマットする
    
    Args:
        value: フォーマットする数値
    Returns:
        str: カンマ区切りでフォーマットされた数値文字列
    """
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return "0"

def format_datetime(value):
    """
    日時を指定のフォーマットで表示する
    
    Args:
        value: datetime オブジェクト
    Returns:
        str: フォーマットされた日時文字列
    """
    if value is None:
        return ""
    try:
        return value.strftime("%Y年%m月%d日 %H:%M")
    except:
        return str(value)

def create_app(config_class=Config):
    """
    アプリケーションファクトリー
    
    Flaskアプリケーションを初期化し、必要な設定と拡張機能を登録する
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # データベースディレクトリの確保
    os.makedirs(app.instance_path, exist_ok=True)
    
    # 拡張機能の初期化
    db.init_app(app)
    
    # LoginManagerの設定
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # user_loaderの追加
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Migrateの設定
    migrate = Migrate()
    migrate.init_app(app, db)
    
    # Blueprintの登録を修正
    from .routes import main_bp, auth_bp, static_bp, settings_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(static_bp)
    app.register_blueprint(settings_bp)
    
    # アプリケーションコンテキスト内でデータベースを作成
    with app.app_context():
        db.create_all()
    
    # テンプレートフィルターの登録
    app.jinja_env.filters['format_number'] = format_number
    app.jinja_env.filters['format_datetime'] = format_datetime
    
    # 静的ファイルの初期設定
    from app.utils.image_setup import setup_default_avatar
    setup_default_avatar()
    
    # ロギング設定
    from app.utils.logging import setup_logging
    setup_logging(app)
    
    return app 