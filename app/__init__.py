# アプリケーションパッケージの初期化
# このファイルはappディレクトリをPythonパッケージとして認識させるために必要です 

from flask import Flask
from .config import Config
from .extensions import db, init_extensions
from flask_login import current_user
import os
from .models.user import User
from .models.business import RevenueBusiness

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
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # SQLAlchemyの初期化を最初に行う
    db.init_app(app)
    
    # その他の拡張機能を初期化
    init_extensions(app)
    
    # Blueprintの登録
    from .routes import main_routes, auth_routes, static_routes, settings_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(static_routes.bp)
    app.register_blueprint(settings_routes.bp)
    
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