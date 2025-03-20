from app import create_app

# アプリケーションのインスタンスを作成
app = create_app()

# 開発サーバーの起動設定
if __name__ == '__main__':
    app.run()
