from flask import Blueprint, render_template
from flask_login import login_required

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/')
@login_required
def index():
    """分析情報のメインページ"""
    return render_template('analysis/index.html') 