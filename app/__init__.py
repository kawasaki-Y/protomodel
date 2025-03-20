# アプリケーションパッケージの初期化
# このファイルはappディレクトリをPythonパッケージとして認識させるために必要です 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from datetime import datetime
from app.extensions import db, login_manager
import os

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

def create_app():
    """
    アプリケーションファクトリー
    
    Flaskアプリケーションを初期化し、必要な設定と拡張機能を登録する
    """
    app = Flask(__name__)
    
    # 設定の読み込み
    app.config.update(
        SECRET_KEY='your-secret-key',
        SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=True
    )
    
    # 拡張機能の初期化
    db.init_app(app)
    
    with app.app_context():
        # データベースのテーブルを作成
        db.create_all()
    
    # LoginManagerの設定
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'ログインが必要です。'
    
    # user_loaderの設定
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Blueprintの登録
    from .routes import main_routes, auth_routes, revenue_plan_routes, settings_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(revenue_plan_routes.bp)
    app.register_blueprint(settings_routes.bp)
    
    # テンプレートフィルターの登録
    app.jinja_env.filters['format_number'] = format_number
    app.jinja_env.filters['format_datetime'] = format_datetime
    
    return app 