from flask import Blueprint, jsonify
from app.models.user import User
from flask_login import login_required, current_user
from app.extensions import db

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/users/<email>')
@login_required
def check_user(email):
    """
    ユーザー情報をデバッグ表示
    注意: 本番環境では削除または保護すること
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "ユーザーが見つかりません"})
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "has_password": user.password_hash is not None,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }) 