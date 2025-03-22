from app import create_app, db

def reset_database():
    app = create_app()
    
    with app.app_context():
        # テーブルの削除
        db.drop_all()
        
        # モデルのインポート
        from app.models.user import User
        from app.models.business import RevenueBusiness, Service, Customer
        from app.models.revenue_plan import RevenuePlan, RevenuePlanDetail
        
        # テーブルの作成
        db.create_all()
        
        print("データベースをリセットしました。")

if __name__ == "__main__":
    reset_database() 