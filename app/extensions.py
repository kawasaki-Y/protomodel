from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# 拡張機能のインスタンス化
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def init_extensions(app):
    """拡張機能の初期化"""
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # LoginManagerの設定
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'このページにアクセスするにはログインが必要です。'

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_message_category = 'warning' 