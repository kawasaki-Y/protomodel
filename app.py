from flask import Flask, render_template
from app.models.models import db, User
from flask_login import LoginManager
import config
import os

def create_app():
    app = Flask(__name__, 
                template_folder='app/templates',
                static_folder='app/static')
    
    # 設定の読み込み
    app.config.from_object(config.Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///business_plan.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'  # 本番環境では環境変数から取得するなど安全な方法で設定すること
    
    # データベースの初期化
    db.init_app(app)
    
    # ログインマネージャーの設定
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'この機能を使用するにはログインが必要です'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ルートの登録
    from app.routes.main_routes import main_bp
    from app.routes.business_plan_routes import business_plan_bp
    from app.routes.cash_flow_routes import cash_flow_bp
    # WeasyPrint問題により一時的にコメントアウト
    # from app.routes.export_routes import export_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.analytics_routes import analytics_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(business_plan_bp)
    app.register_blueprint(cash_flow_bp)
    # WeasyPrint問題により一時的にコメントアウト
    # app.register_blueprint(export_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analytics_bp)
    
    # データベース作成
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001) 