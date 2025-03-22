from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/settings')
@login_required
def index():
    """設定画面のインデックスページ"""
    return render_template('settings/index.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('settings/profile.html')

@bp.route('/security')
@login_required
def security():
    return render_template('settings/security.html')