from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# 単一のインスタンスを作成
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def init_extensions(app):
    # db.init_app(app)は__init__.pyで行うため、ここでは行わない
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'このページにアクセスするにはログインが必要です。'
    login_manager.login_message_category = 'warning' 