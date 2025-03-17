from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import db, BusinessPlan, BusinessPlanItem
from app.models.revenue_business import RevenueBusiness
from app.models.sales_record import SalesRecord
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

@numerical_plan_bp.route('/revenue-model')
@login_required
def revenue_model():
    """収益モデル作成ページ"""
    return render_template('numerical_plan/revenue_model.html')

@numerical_plan_bp.route('/revenue-wizard')
@login_required
def revenue_wizard():
    """収益モデル診断ウィザード"""
    return render_template('numerical_plan/revenue_wizard.html')

@numerical_plan_bp.route('/create-revenue-model', methods=['GET', 'POST'])
@login_required
def create_revenue_model():
    """収益モデル作成"""
    if request.method == 'POST':
        # POSTリクエストの処理
        pass
    return render_template('numerical_plan/create_revenue_model.html')

@numerical_plan_bp.route('/revenue/sales')
@login_required
def sales_entry():
    """
    売上高入力画面
    
    ユーザーが保有する収益事業モデルの一覧を表示し、
    売上データの入力を可能にする
    """
    revenue_businesses = RevenueBusiness.query.filter_by(user_id=current_user.id).all()
    return render_template('numerical_plan/revenue/sales.html', revenue_businesses=revenue_businesses)

@numerical_plan_bp.route('/api/revenue-businesses')
@login_required
def get_revenue_businesses():
    """収益事業モデルの一覧を取得するAPI"""
    businesses = RevenueBusiness.query.filter_by(user_id=current_user.id).all()
    return jsonify([business.to_dict() for business in businesses])

@numerical_plan_bp.route('/api/sales-records/<int:business_id>')
@login_required
def get_sales_records(business_id):
    """
    特定の収益事業の売上記録を取得するAPI
    
    Parameters:
        business_id (int): 収益事業のID
    """
    # 事業の所有者確認
    business = RevenueBusiness.query.get_or_404(business_id)
    if business.user_id != current_user.id:
        return jsonify({'error': '権限がありません'}), 403
    
    records = SalesRecord.query.filter_by(revenue_business_id=business_id).all()
    return jsonify([record.to_dict() for record in records])

@numerical_plan_bp.route('/api/sales-records', methods=['POST'])
@login_required
def save_sales_record():
    """
    売上記録を保存するAPI
    
    既存の記録がある場合は更新し、ない場合は新規作成する
    """
    data = request.get_json()
    
    # 事業の所有者確認
    business = RevenueBusiness.query.get_or_404(data['revenue_business_id'])
    if business.user_id != current_user.id:
        return jsonify({'error': '権限がありません'}), 403
    
    try:
        # 既存の記録を検索または新規作成
        record = SalesRecord.query.filter_by(
            revenue_business_id=data['revenue_business_id'],
            month=datetime.strptime(data['month'], '%Y-%m').date()
        ).first() or SalesRecord(
            revenue_business_id=data['revenue_business_id'],
            month=datetime.strptime(data['month'], '%Y-%m').date()
        )
        
        # データの更新
        for key, value in data.items():
            if hasattr(record, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(record, key, value)
        
        if not record.id:
            db.session.add(record)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '売上記録を保存しました',
            'record': record.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'保存中にエラーが発生しました: {str(e)}'
        }), 400 