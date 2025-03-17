from flask import Blueprint, render_template
from flask_login import login_required

capital_policy_bp = Blueprint('capital_policy', __name__)

@capital_policy_bp.route('/')
@login_required
def index():
    """資本政策のメインページ"""
    return render_template('capital_policy/index.html') 