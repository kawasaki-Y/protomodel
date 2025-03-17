# アプリケーションパッケージの初期化
# このファイルはappディレクトリをPythonパッケージとして認識させるために必要です 

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# dbオブジェクトをここで初期化
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # 設定の読み込み
    app.config['SECRET_KEY'] = 'your-secret-key'  # 本番環境では環境変数から読み込むことを推奨
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 拡張機能の初期化
    db.init_app(app)
    login_manager.init_app(app)
    
    # ログイン設定
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'このページにアクセスするにはログインが必要です。'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    with app.app_context():
        # モデルのインポート（順序が重要）
        from app.models.user import User
        from app.models.revenue_business import RevenueBusiness
        from app.models.sales_record import SalesRecord
        
        # ブループリントの登録
        from app.routes.auth_routes import auth_bp
        from app.routes.numerical_plan_routes import numerical_plan_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(numerical_plan_bp)
        
        # データベースの作成
        db.create_all()
        
        # テストユーザーの作成（開発時のみ）
        if not User.query.filter_by(username='test').first():
            test_user = User(
                username='test',
                email='test@example.com'
            )
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
    
    return app 