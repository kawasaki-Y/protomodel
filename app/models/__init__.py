# モデルパッケージの初期化
# このファイルはapp/modelsディレクトリをPythonパッケージとして認識させるために必要です 

from app.extensions import db

# 基本モデルを先にインポート
from app.models.user import User
from app.models.business import RevenueBusiness, Service, Customer

# 依存するモデルを後でインポート
from app.models.revenue_plan import RevenuePlan, RevenuePlanValue

# 必要に応じて他のモデルをインポート

__all__ = [
    'User',
    'RevenueBusiness',
    'Service',
    'Customer',
    'RevenuePlan',
    'RevenuePlanValue'
] 