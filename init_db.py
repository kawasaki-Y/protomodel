from app import create_app
from app.extensions import db
from app.models.user import User

def init_database():
    app = create_app()
    with app.app_context():
        # データベースの再作成
        db.drop_all()  # 既存のテーブルを削除
        db.create_all()  # テーブルを新規作成
        
        # テストユーザーの作成
        test_user = User(
            username='test_user',
            email='test@example.com'
        )
        test_user.set_password('password123')
        
        try:
            db.session.add(test_user)
            db.session.commit()
            print("テストユーザーを作成しました")
            print("Email: test@example.com")
            print("Password: password123")
        except Exception as e:
            print(f"エラー: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_database() 