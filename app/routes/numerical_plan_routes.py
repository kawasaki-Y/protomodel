from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models.models import db, BusinessPlan, BusinessPlanItem

numerical_plan_bp = Blueprint('numerical_plan', __name__, url_prefix='/numerical-plan')

@numerical_plan_bp.route('/')
@login_required
def index():
    """数値計画のメインページを表示"""
    return render_template('numerical_plan/index.html')

@numerical_plan_bp.route('/revenue/<category>')
@login_required
def revenue_plan(category):
    """収益計画の各カテゴリページを表示"""
    categories = {
        'sales': '売上高',
        'non_operating': '営業外収益',
        'special': '特別利益'
    }
    if category not in categories:
        return jsonify({'error': '無効なカテゴリです'}), 400
    return render_template('numerical_plan/revenue.html', category=category, category_name=categories[category])

@numerical_plan_bp.route('/expense/<category>')
@login_required
def expense_plan(category):
    """費用計画の各カテゴリページを表示"""
    categories = {
        'cost': '売上原価',
        'sga': '販管費',
        'non_operating': '営業外費用',
        'special': '特別損失'
    }
    if category not in categories:
        return jsonify({'error': '無効なカテゴリです'}), 400
    return render_template('numerical_plan/expense.html', category=category, category_name=categories[category])

@numerical_plan_bp.route('/api/revenue-plan', methods=['GET'])
@login_required
def get_revenue_plan():
    """収益計画のデータを取得"""
    business_plan = BusinessPlan.query.filter_by(user_id=current_user.id).first()
    if not business_plan:
        return jsonify({'error': '事業計画が見つかりません'}), 404
    
    items = BusinessPlanItem.query.filter_by(
        business_plan_id=business_plan.id,
        category='revenue'
    ).all()
    
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'amounts': [item.get_month_amount(i) for i in range(1, 13)]
    } for item in items])

@numerical_plan_bp.route('/api/expense-plan', methods=['GET'])
@login_required
def get_expense_plan():
    """費用計画のデータを取得"""
    business_plan = BusinessPlan.query.filter_by(user_id=current_user.id).first()
    if not business_plan:
        return jsonify({'error': '事業計画が見つかりません'}), 404
    
    items = BusinessPlanItem.query.filter_by(
        business_plan_id=business_plan.id,
        category='expense'
    ).all()
    
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'amounts': [item.get_month_amount(i) for i in range(1, 13)]
    } for item in items])

@numerical_plan_bp.route('/api/plan-items', methods=['POST'])
@login_required
def update_plan_items():
    """計画項目の更新"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'データが提供されていません'}), 400
    
    business_plan = BusinessPlan.query.filter_by(user_id=current_user.id).first()
    if not business_plan:
        return jsonify({'error': '事業計画が見つかりません'}), 404
    
    item_id = data.get('id')
    amounts = data.get('amounts', [])
    
    if not item_id or not amounts or len(amounts) != 12:
        return jsonify({'error': '無効なデータ形式です'}), 400
    
    item = BusinessPlanItem.query.get(item_id)
    if not item or item.business_plan_id != business_plan.id:
        return jsonify({'error': '項目が見つかりません'}), 404
    
    for month, amount in enumerate(amounts, start=1):
        item.set_month_amount(month, amount)
    
    db.session.commit()
    return jsonify({'success': True}) 