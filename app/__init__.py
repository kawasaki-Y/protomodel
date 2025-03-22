# アプリケーションパッケージの初期化
# このファイルはappディレクトリをPythonパッケージとして認識させるために必要です 

from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate
from flask_login import current_user
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

def create_app(config_class=Config):
    """
    アプリケーションファクトリー
    
    Flaskアプリケーションを初期化し、必要な設定と拡張機能を登録する
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Blueprintの登録
    from app.routes.main_routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.auth_routes import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.business_routes import bp as business_bp
    app.register_blueprint(business_bp)
    
    # 設定ルートを登録
    from app.routes.settings_routes import bp as settings_bp
    app.register_blueprint(settings_bp)
    
    # 静的ファイルのルートを登録
    from app.routes.static_routes import bp as static_bp
    app.register_blueprint(static_bp)
    
    # アプリケーションコンテキスト内でモデルを初期化
    with app.app_context():
        from app.models.user import User
        from app.models.business import RevenueBusiness, Service, Customer
        from app.models.revenue_plan import RevenuePlan, RevenuePlanDetail
        
        # データベースの作成
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