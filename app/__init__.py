# アプリケーションパッケージの初期化
# このファイルはappディレクトリをPythonパッケージとして認識させるために必要です 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from datetime import datetime
from app.extensions import db, login_manager  # dbとlogin_managerをextensionsから取得
from app.routes.revenue_plan_routes import revenue_plan_bp

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
    app.config.from_object(Config)

    # 拡張機能の初期化
    db.init_app(app)
    login_manager.init_app(app)
    
    # ログイン設定
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'このページにアクセスするにはログインが必要です。'

    # カスタムフィルターの登録
    app.jinja_env.filters['format_number'] = format_number
    app.jinja_env.filters['datetime'] = format_datetime

    with app.app_context():
        # Blueprintの登録
        from app.routes.auth_routes import auth_bp
        from app.routes.main_routes import main_bp
        from app.routes.numerical_plan_routes import numerical_plan_bp
        from app.routes.business_plan_routes import business_plan_bp
        from app.routes.future_plan_routes import future_plan_bp
        from app.routes.cash_flow_routes import cash_flow_bp
        from app.routes.capital_policy_routes import capital_policy_bp
        from app.routes.analysis_routes import analysis_bp
        from app.routes.reports_routes import reports_bp
        from app.routes.account_routes import account_bp
        from app.routes.settings_routes import settings_bp
        from app.routes.revenue_model_routes import revenue_model_bp
        from app.routes.revenue_plan_routes import revenue_plan_bp
        from app.routes.debug_routes import debug_bp

        # 各Blueprintを登録
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(numerical_plan_bp, url_prefix='/numerical-plan')
        app.register_blueprint(business_plan_bp, url_prefix='/business-plan')
        app.register_blueprint(future_plan_bp, url_prefix='/future-plan')
        app.register_blueprint(cash_flow_bp, url_prefix='/cash-flow')
        app.register_blueprint(capital_policy_bp, url_prefix='/capital-policy')
        app.register_blueprint(analysis_bp, url_prefix='/analysis')
        app.register_blueprint(reports_bp, url_prefix='/reports')
        app.register_blueprint(account_bp, url_prefix='/account')
        app.register_blueprint(settings_bp, url_prefix='/settings')
        app.register_blueprint(revenue_model_bp)
        app.register_blueprint(revenue_plan_bp)
        app.register_blueprint(debug_bp)

        # データベースの作成
        db.create_all()

    return app

# ユーザーローダーの設定
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id)) 