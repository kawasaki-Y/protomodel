from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models.models import db, BusinessPlan, BusinessPlanItem, CashFlowPlan, CashFlowItem
from flask_login import login_required, current_user
from datetime import datetime
import json

cash_flow_bp = Blueprint('cash_flow', __name__, url_prefix='/cash-flow')

@cash_flow_bp.route('/')
@login_required
def index():
    """資金繰り計画一覧"""
    # ユーザーに関連する事業計画を取得
    business_plans = BusinessPlan.query.filter_by(user_id=current_user.id).all()
    # 資金繰り計画一覧を取得
    cash_flow_plans = CashFlowPlan.query.filter(
        CashFlowPlan.business_plan_id.in_([bp.id for bp in business_plans])
    ).all() if business_plans else []
    
    return render_template('cash_flow/index.html', cash_flow_plans=cash_flow_plans, business_plans=business_plans)

@cash_flow_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """資金繰り計画作成"""
    if request.method == 'POST':
        data = request.form
        business_plan_id = data.get('business_plan_id')
        name = data.get('name')
        
        # 新しい資金繰り計画を作成
        new_plan = CashFlowPlan(
            business_plan_id=business_plan_id,
            name=name,
            fiscal_year=datetime.now().year
        )
        db.session.add(new_plan)
        db.session.commit()
        
        return redirect(url_for('cash_flow.view', plan_id=new_plan.id))
    
    # GETの場合は作成フォームを表示
    # 関連する事業計画の一覧を取得
    business_plans = BusinessPlan.query.filter_by(user_id=current_user.id).all()
    
    return render_template('cash_flow/create.html', business_plans=business_plans)

@cash_flow_bp.route('/<int:plan_id>')
@login_required
def view(plan_id):
    """資金繰り計画詳細表示"""
    plan = CashFlowPlan.query.get_or_404(plan_id)
    
    # アクセス権確認
    if plan.business_plan and plan.business_plan.user_id != current_user.id:
        flash('このプランへのアクセス権がありません', 'danger')
        return redirect(url_for('cash_flow.index'))
    
    root_items = CashFlowItem.query.filter_by(
        cash_flow_plan_id=plan_id, 
        parent_id=None
    ).order_by(CashFlowItem.sort_order).all()
    
    return render_template('cash_flow/view.html', plan=plan, root_items=root_items)

@cash_flow_bp.route('/api/items/<int:plan_id>')
@login_required
def get_items(plan_id):
    """資金繰り計画項目を取得するAPI"""
    # アクセス権確認
    plan = CashFlowPlan.query.get_or_404(plan_id)
    if plan.business_plan and plan.business_plan.user_id != current_user.id:
        return jsonify({'error': 'アクセス権がありません'}), 403
    
    root_items = CashFlowItem.query.filter_by(
        cash_flow_plan_id=plan_id, 
        parent_id=None
    ).order_by(CashFlowItem.sort_order).all()
    
    items_data = []
    for root in root_items:
        item_data = {
            'id': root.id,
            'name': root.name,
            'category': root.category,
            'type': root.item_type,
            'sort_order': root.sort_order,
            'children': []
        }
        
        # 子項目を追加
        children = CashFlowItem.query.filter_by(parent_id=root.id).order_by(CashFlowItem.sort_order).all()
        for child in children:
            child_data = {
                'id': child.id,
                'name': child.name,
                'category': child.category,
                'type': child.item_type,
                'sort_order': child.sort_order
            }
            item_data['children'].append(child_data)
        
        items_data.append(item_data)
    
    return jsonify(items_data)

@cash_flow_bp.route('/api/item/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    """資金繰り計画項目の取得"""
    item = CashFlowItem.query.get_or_404(item_id)
    
    # アクセス権確認
    plan = CashFlowPlan.query.get(item.cash_flow_plan_id)
    if plan.business_plan and plan.business_plan.user_id != current_user.id:
        return jsonify({'error': 'アクセス権がありません'}), 403
    
    # 項目の詳細情報をJSON形式で返す
    item_data = {
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'item_type': item.item_type,
        'description': item.description,
        'parent_id': item.parent_id
    }
    
    return jsonify(item_data)

@cash_flow_bp.route('/api/item', methods=['POST'])
@login_required
def create_item():
    """資金繰り計画項目の新規作成"""
    data = request.json
    
    # アクセス権確認
    plan = CashFlowPlan.query.get(data.get('cash_flow_plan_id'))
    if not plan or (plan.business_plan and plan.business_plan.user_id != current_user.id):
        return jsonify({'error': 'アクセス権がありません'}), 403
    
    new_item = CashFlowItem(
        cash_flow_plan_id=data.get('cash_flow_plan_id'),
        parent_id=data.get('parent_id'),
        category=data.get('category'),
        item_type=data.get('item_type', 'detail'),
        name=data.get('name'),
        description=data.get('description', ''),
        sort_order=data.get('sort_order', 0)
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({'id': new_item.id, 'success': True})

@cash_flow_bp.route('/api/item/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """資金繰り計画項目の更新"""
    item = CashFlowItem.query.get_or_404(item_id)
    
    # アクセス権確認
    plan = CashFlowPlan.query.get(item.cash_flow_plan_id)
    if plan.business_plan and plan.business_plan.user_id != current_user.id:
        return jsonify({'error': 'アクセス権がありません'}), 403
    
    data = request.json
    
    # 基本情報の更新
    if 'name' in data: item.name = data['name']
    if 'category' in data: item.category = data['category']
    if 'description' in data: item.description = data['description']
    
    db.session.commit()
    
    return jsonify({'success': True})

@cash_flow_bp.route('/api/item/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """資金繰り計画項目の削除"""
    item = CashFlowItem.query.get_or_404(item_id)
    
    # アクセス権確認
    plan = CashFlowPlan.query.get(item.cash_flow_plan_id)
    if plan.business_plan and plan.business_plan.user_id != current_user.id:
        return jsonify({'error': 'アクセス権がありません'}), 403
    
    # 子項目も一緒に削除（SQLAlchemyのカスケード設定があるためDB上では自動的に削除される）
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'success': True})

@cash_flow_bp.route('/sync-with-business-plan/<int:cash_flow_id>', methods=['POST'])
@login_required
def sync_with_business_plan(cash_flow_id):
    """事業計画から資金繰り計画へ数値を反映"""
    cash_flow_plan = CashFlowPlan.query.get_or_404(cash_flow_id)
    
    # 事業計画から売上と費用の項目を取得
    sales_items = PlanItem.query.filter_by(
        business_plan_id=cash_flow_plan.business_plan_id, 
        category='売上'
    ).all()
    
    expense_items = PlanItem.query.filter_by(
        business_plan_id=cash_flow_plan.business_plan_id, 
        category='原価'
    ).all()
    expense_items.extend(PlanItem.query.filter_by(
        business_plan_id=cash_flow_plan.business_plan_id, 
        category='販管費'
    ).all())
    
    # 資金繰り計画の対応する項目を更新
    # 売上の反映例（実際のアプリではルールに基づいた複雑な処理が必要）
    for sales_item in sales_items:
        # 関連付けられた資金繰り項目を検索
        cf_item = CashFlowItem.query.filter_by(
            cash_flow_plan_id=cash_flow_plan.id,
            related_plan_item_id=sales_item.id
        ).first()
        
        if cf_item:
            # 月ごとの金額を分配（例：月末に100%計上）
            # 1月の例
            cf_item.m1_end = sales_item.m1_amount
            # 2月の例（実際のアプリでは3月～12月も同様に処理）
            cf_item.m2_end = sales_item.m2_amount
    
    # 費用の反映も同様に処理
    # ...
    
    db.session.commit()
    
    return jsonify({'success': True})

def create_default_cash_flow_items(cash_flow_plan_id, business_plan_id):
    """新規資金繰り計画の初期項目を作成する補助関数"""
    # 親項目の作成
    root_categories = [
        {'name': '期首現金残高', 'category': '現金残高', 'item_type': 'header', 'sort_order': 10},
        {'name': '営業収入', 'category': '営業収入', 'item_type': 'header', 'sort_order': 20},
        {'name': '営業支出', 'category': '営業支出', 'item_type': 'header', 'sort_order': 30},
        {'name': '営業キャッシュフロー', 'category': '営業CF', 'item_type': 'header', 'sort_order': 40},
        {'name': '投資収入', 'category': '投資収入', 'item_type': 'header', 'sort_order': 50},
        {'name': '投資支出', 'category': '投資支出', 'item_type': 'header', 'sort_order': 60},
        {'name': '投資キャッシュフロー', 'category': '投資CF', 'item_type': 'header', 'sort_order': 70},
        {'name': '財務収入', 'category': '財務収入', 'item_type': 'header', 'sort_order': 80},
        {'name': '財務支出', 'category': '財務支出', 'item_type': 'header', 'sort_order': 90},
        {'name': '財務キャッシュフロー', 'category': '財務CF', 'item_type': 'header', 'sort_order': 100},
        {'name': '当月キャッシュフロー', 'category': '当月CF', 'item_type': 'header', 'sort_order': 110},
        {'name': '期末現金残高', 'category': '現金残高', 'item_type': 'header', 'sort_order': 120},
    ]
    
    # 親項目のIDマップ（子項目作成のため）
    parent_id_map = {}
    
    # 親項目の作成
    for category_data in root_categories:
        item = CashFlowItem(
            cash_flow_plan_id=cash_flow_plan_id,
            parent_id=None,
            **category_data
        )
        db.session.add(item)
        db.session.flush()  # IDを取得するためフラッシュ
        parent_id_map[category_data['category']] = item.id
    
    # 事業計画から関連項目を取得して子項目を作成
    # 売上項目
    sales_items = PlanItem.query.filter_by(business_plan_id=business_plan_id, category='売上', item_type='detail').all()
    for idx, sales_item in enumerate(sales_items):
        item = CashFlowItem(
            cash_flow_plan_id=cash_flow_plan_id,
            parent_id=parent_id_map.get('営業収入'),
            related_plan_item_id=sales_item.id,
            category='営業収入',
            item_type='detail',
            name=f"{sales_item.name}売上",
            sort_order=idx + 1
        )
        db.session.add(item)
    
    # 費用項目（原価・販管費）も同様に処理
    expense_items = PlanItem.query.filter_by(business_plan_id=business_plan_id, category='原価', item_type='detail').all()
    expense_items.extend(PlanItem.query.filter_by(business_plan_id=business_plan_id, category='販管費', item_type='detail').all())
    
    for idx, expense_item in enumerate(expense_items):
        item = CashFlowItem(
            cash_flow_plan_id=cash_flow_plan_id,
            parent_id=parent_id_map.get('営業支出'),
            related_plan_item_id=expense_item.id,
            category='営業支出',
            item_type='detail',
            name=f"{expense_item.name}支出",
            sort_order=idx + 1
        )
        db.session.add(item)
    
    # 財務活動の典型的な項目
    financial_items = [
        {'name': '借入金', 'category': '財務収入', 'parent_key': '財務収入', 'sort_order': 1, 'item_type': 'detail'},
        {'name': '返済', 'category': '財務支出', 'parent_key': '財務支出', 'sort_order': 1, 'item_type': 'detail'},
    ]
    
    for fin_item in financial_items:
        parent_key = fin_item.pop('parent_key')
        item = CashFlowItem(
            cash_flow_plan_id=cash_flow_plan_id,
            parent_id=parent_id_map.get(parent_key),
            **fin_item
        )
        db.session.add(item)
    
    db.session.commit() 