import os
import base64
import logging

def setup_default_avatar():
    """
    デフォルトアバター画像を設定します
    """
    # 画像ディレクトリの確認
    img_dir = os.path.join('app', 'static', 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    
    # デフォルトアバターのパス
    avatar_path = os.path.join(img_dir, 'default-avatar.png')
    
    # 既に存在すれば何もしない
    if os.path.exists(avatar_path):
        return
    
    # Base64エンコードされた非常にシンプルなアバター画像
    # 青い円に白い「U」の文字が入った200x200のPNG
    avatar_base64 = """
    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
    """
    
    try:
        # Base64デコードして画像ファイルを保存
        image_data = base64.b64decode(avatar_base64.strip())
        with open(avatar_path, 'wb') as f:
            f.write(image_data)
        logging.info(f"デフォルトアバター画像を作成しました: {avatar_path}")
    except Exception as e:
        logging.error(f"アバター画像の作成に失敗しました: {str(e)}")
        
        # 失敗した場合は空のファイルを作成して404を防ぐ
        try:
            with open(avatar_path, 'wb') as f:
                # 最小限のPNG画像データ (1x1 透明ピクセル)
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
            logging.info(f"最小限のPNG画像を作成しました: {avatar_path}")
        except Exception as e2:
            logging.error(f"画像ファイルの作成に失敗しました: {str(e2)}") 