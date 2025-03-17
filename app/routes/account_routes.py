from flask import Blueprint, render_template
from flask_login import login_required

account_bp = Blueprint('account', __name__)

@account_bp.route('/')
@login_required
def index():
    """勘定科目設定のメインページ"""
    return render_template('account/index.html') 