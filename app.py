from app import create_app

# アプリケーションのインスタンスを作成
app = create_app()

# 開発サーバーの起動設定
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5003,  # ポートを5003に変更
        debug=True,  # デバッグモードを有効化
        use_reloader=True,
        use_debugger=True,  # デバッガーを有効化して詳細なエラー情報を表示
        threaded=True  # スレッド処理を有効化
    )
