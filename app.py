from app import create_app

# アプリケーションのインスタンスを作成
app = create_app()

# 開発サーバーの起動設定
if __name__ == '__main__':
    # デバッグモードを有効にし、全てのインターフェースからアクセス可能に
    # ポート5001を使用（一般的な5000は他のサービスと競合することが多いため）
    app.run(debug=True, host='0.0.0.0', port=5001)
