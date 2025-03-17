from flask import Blueprint, render_template
from flask_login import login_required

future_plan_bp = Blueprint('future_plan', __name__)

@future_plan_bp.route('/')
@login_required
def index():
    return render_template('future_plan/index.html') 