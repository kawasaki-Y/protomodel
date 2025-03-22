from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# SQLAlchemyインスタンスを初期化
db = SQLAlchemy()
migrate = Migrate()

# LoginManagerインスタンスを初期化
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'この機能を利用するにはログインが必要です。' 