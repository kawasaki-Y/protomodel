from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.models import db, BusinessPlan, CashFlowPlan, CashFlowItem, PlanItem
from flask_login import login_required, current_user
import json

cash_flow_bp = Blueprint('cash_flow', __name__, url_prefix='/cash-flow')

@cash_flow_bp.route('/')
@login_required
def cash_flow():
    """資金繰り計画画面"""
    # 直近の単年事業計画とそれに紐づく資金繰り計画を取得
    business_plan = BusinessPlan.query.filter_by(plan_type='current').order_by(BusinessPlan.created_at.desc()).first()
    
    if not business_plan:
        # 事業計画がない場合は、事業計画の作成を促す
        return render_template('cash_flow/no_business_plan.html')
    
    # 資金繰り計画を取得（なければ作成）
    cash_flow_plan = CashFlowPlan.query.filter_by(business_plan_id=business_plan.id).first()
    if not cash_flow_plan:
        # 資金繰り計画を新規作成
        cash_flow_plan = CashFlowPlan(
            business_plan_id=business_plan.id,
            name=f"{business_plan.name}の資金繰り計画",
            fiscal_year=business_plan.fiscal_year
        )
        db.session.add(cash_flow_plan)
        db.session.commit()
        
        # 初期項目を作成
        create_default_cash_flow_items(cash_flow_plan.id, business_plan.id)
    
    # ルート項目（親項目）を取得
    root_items = CashFlowItem.query.filter_by(cash_flow_plan_id=cash_flow_plan.id, parent_id=None).order_by(CashFlowItem.sort_order).all()
    
    # 月の表示ラベルを作成（5日区切り）
    months_days = []
    labels = ["5日", "10日", "15日", "20日", "25日", "末日"]
    
    month_num = business_plan.start_month
    for _ in range(12):  # 12ヶ月分
        for label in labels:
            months_days.append(f"{month_num}月{label}")
        month_num = (month_num % 12) + 1
    
    # 関連事業計画項目のデータを取得
    plan_items = PlanItem.query.filter_by(business_plan_id=business_plan.id).all()
    plan_items_data = []
    for item in plan_items:
        plan_items_data.append({
            'id': item.id,
            'name': item.name,
            'category': item.category
        })
    plan_items_json = json.dumps(plan_items_data)
    
    return render_template('cash_flow/view.html', 
                          business_plan=business_plan,
                          cash_flow_plan=cash_flow_plan,
                          root_items=root_items,
                          months_days=months_days,
                          plan_items_json=plan_items_json)

@cash_flow_bp.route('/item/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    """資金繰り計画項目の取得"""
    item = CashFlowItem.query.get_or_404(item_id)
    
    # 項目の詳細情報をJSON形式で返す
    item_data = {
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'item_type': item.item_type,
        'description': item.description,
        'parent_id': item.parent_id,
        'related_plan_item_id': item.related_plan_item_id,
        # 1月の金額
        'm1': {
            'd5': item.m1_d5,
            'd10': item.m1_d10,
            'd15': item.m1_d15,
            'd20': item.m1_d20,
            'd25': item.m1_d25,
            'end': item.m1_end
        },
        # 2月の金額
        'm2': {
            'd5': item.m2_d5,
            'd10': item.m2_d10,
            'd15': item.m2_d15,
            'd20': item.m2_d20,
            'd25': item.m2_d25,
            'end': item.m2_end
        }
        # 注: 実際のアプリでは3月～12月も同様に定義
    }
    
    return jsonify(item_data)

@cash_flow_bp.route('/item', methods=['POST'])
@login_required
def create_item():
    """資金繰り計画項目の新規作成"""
    data = request.json
    
    new_item = CashFlowItem(
        cash_flow_plan_id=data.get('cash_flow_plan_id'),
        parent_id=data.get('parent_id'),
        related_plan_item_id=data.get('related_plan_item_id'),
        category=data.get('category'),
        item_type=data.get('item_type', 'detail'),
        name=data.get('name'),
        description=data.get('description', ''),
        sort_order=data.get('sort_order', 0)
    )
    
    # 月別・日別金額があれば設定（1月の例）
    m1 = data.get('m1', {})
    if 'd5' in m1: new_item.m1_d5 = m1['d5']
    if 'd10' in m1: new_item.m1_d10 = m1['d10']
    if 'd15' in m1: new_item.m1_d15 = m1['d15']
    if 'd20' in m1: new_item.m1_d20 = m1['d20']
    if 'd25' in m1: new_item.m1_d25 = m1['d25']
    if 'end' in m1: new_item.m1_end = m1['end']
    
    # 2月の例（実際のアプリでは3月～12月も同様に処理）
    m2 = data.get('m2', {})
    if 'd5' in m2: new_item.m2_d5 = m2['d5']
    if 'd10' in m2: new_item.m2_d10 = m2['d10']
    if 'd15' in m2: new_item.m2_d15 = m2['d15']
    if 'd20' in m2: new_item.m2_d20 = m2['d20']
    if 'd25' in m2: new_item.m2_d25 = m2['d25']
    if 'end' in m2: new_item.m2_end = m2['end']
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({'id': new_item.id, 'success': True})

@cash_flow_bp.route('/item/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """資金繰り計画項目の更新"""
    item = CashFlowItem.query.get_or_404(item_id)
    data = request.json
    
    # 基本情報の更新
    if 'name' in data: item.name = data['name']
    if 'category' in data: item.category = data['category']
    if 'description' in data: item.description = data['description']
    if 'related_plan_item_id' in data: item.related_plan_item_id = data['related_plan_item_id']
    
    # 月別・日別金額の更新（1月の例）
    m1 = data.get('m1', {})
    if 'd5' in m1: item.m1_d5 = m1['d5']
    if 'd10' in m1: item.m1_d10 = m1['d10']
    if 'd15' in m1: item.m1_d15 = m1['d15']
    if 'd20' in m1: item.m1_d20 = m1['d20']
    if 'd25' in m1: item.m1_d25 = m1['d25']
    if 'end' in m1: item.m1_end = m1['end']
    
    # 2月の例（実際のアプリでは3月～12月も同様に処理）
    m2 = data.get('m2', {})
    if 'd5' in m2: item.m2_d5 = m2['d5']
    if 'd10' in m2: item.m2_d10 = m2['d10']
    if 'd15' in m2: item.m2_d15 = m2['d15']
    if 'd20' in m2: item.m2_d20 = m2['d20']
    if 'd25' in m2: item.m2_d25 = m2['d25']
    if 'end' in m2: item.m2_end = m2['end']
    
    db.session.commit()
    
    return jsonify({'success': True})

@cash_flow_bp.route('/item/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """資金繰り計画項目の削除"""
    item = CashFlowItem.query.get_or_404(item_id)
    
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