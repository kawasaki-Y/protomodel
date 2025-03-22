from app import create_app, db

app = create_app()

# アプリケーションコンテキスト内でFalskSQLAlchemyの初期化を確認
with app.app_context():
    # モデルのインポートとテーブル作成
    from app.models.user import User
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 