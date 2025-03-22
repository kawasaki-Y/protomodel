# ルートパッケージの初期化
# このファイルはapp/routesディレクトリをPythonパッケージとして認識させるために必要です 

from .main_routes import bp as main_bp
from .auth_routes import bp as auth_bp
from .static_routes import bp as static_bp
from .settings_routes import bp as settings_bp

__all__ = ['main_bp', 'auth_bp', 'static_bp', 'settings_bp'] 