# アプリケーションパッケージの初期化
# このファイルはappディレクトリをPythonパッケージとして認識させるために必要です 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# データベースとログイン管理の初期化
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    アプリケーションファクトリー
    
    Flaskアプリケーションを初期化し、必要な設定を行う
    """
    # Flaskアプリケーションの作成
    app = Flask(__name__)
    
    # 基本設定
    app.config['SECRET_KEY'] = 'your-secret-key'  # セッション管理用の秘密鍵
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # SQLiteデータベースの設定
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # パフォーマンス向上のため無効化
    
    # 拡張機能の初期化
    db.init_app(app)  # データベース
    login_manager.init_app(app)  # ログイン管理
    
    # ログイン管理の設定
    login_manager.login_view = 'auth.login'  # ログインページのエンドポイント
    login_manager.login_message = 'このページにアクセスするにはログインが必要です。'
    
    # ユーザーローダーの設定
    @login_manager.user_loader
    def load_user(user_id):
        """ログインユーザーの取得"""
        from app.models.user import User
        return User.query.get(int(user_id))
    
    with app.app_context():
        # 必要なモデルのインポート
        from app.models.user import User
        from app.models.revenue_business import RevenueBusiness
        from app.models.sales_record import SalesRecord
        
        # ブループリントの登録
        from app.routes.auth_routes import auth_bp
        from app.routes.numerical_plan_routes import numerical_plan_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(numerical_plan_bp)
        
        # データベースの初期化
        db.create_all()
        
        # 開発用のテストユーザー作成
        if not User.query.filter_by(username='test').first():
            test_user = User(username='test', email='test@example.com')
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
    
    return app 