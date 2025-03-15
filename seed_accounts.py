#!/usr/bin/env python3
import os
import sys

# プロジェクトルートディレクトリを追加
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

# app.pyからcreate_app関数をインポート
import importlib.util
spec = importlib.util.spec_from_file_location("app", os.path.join(current_dir, "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
create_app = app_module.create_app

# モデルとシードデータ関数をインポート
from app.models.models import db, AccountItem
from app.models.seed_data import seed_account_items

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_account_items() 