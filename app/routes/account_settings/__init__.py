# 勘定科目設定用のブループリント初期化

from flask import Blueprint

account_settings_bp = Blueprint('account_settings', __name__, url_prefix='/account-settings')

from app.routes.account_settings import routes 