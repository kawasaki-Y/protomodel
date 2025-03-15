from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.models import db, BusinessPlan, PlanItem
from datetime import datetime
from flask_login import login_required, current_user

business_plan_bp = Blueprint('business_plan', __name__, url_prefix='/business-plan')

@business_plan_bp.route('/current')
@login_required
def current_plan():
    """単年事業計画画面"""
    # 直近の単年事業計画を取得
    plan = BusinessPlan.query.filter_by(plan_type='current').order_by(BusinessPlan.created_at.desc()).first()
    
    # 事業計画が存在しない場合は新規作成フォームを表示
    if not plan:
        return render_template('business_plan/create.html', plan_type='current', now=datetime.now())
    
    # ルート項目（親項目）を取得
    root_items = PlanItem.query.filter_by(business_plan_id=plan.id, parent_id=None).order_by(PlanItem.sort_order).all()
    
    # 月の表示ラベルを作成
    months = []
    month_num = plan.start_month
    for _ in range(12):  # 12ヶ月分
        months.append(f"{month_num}月")
        month_num = (month_num % 12) + 1
    
    return render_template('business_plan/view.html', 
                          plan=plan,
                          root_items=root_items,
                          months=months)

@business_plan_bp.route('/next')
@login_required
def next_plan():
    """来期事業計画画面"""
    # 直近の来期事業計画を取得
    plan = BusinessPlan.query.filter_by(plan_type='next').order_by(BusinessPlan.created_at.desc()).first()
    
    # 事業計画が存在しない場合は新規作成フォームを表示
    if not plan:
        return render_template('business_plan/create.html', plan_type='next', now=datetime.now())
    
    # ルート項目（親項目）を取得
    root_items = PlanItem.query.filter_by(business_plan_id=plan.id, parent_id=None).order_by(PlanItem.sort_order).all()
    
    # 月の表示ラベルを作成
    months = []
    month_num = plan.start_month
    for _ in range(12):  # 12ヶ月分
        months.append(f"{month_num}月")
        month_num = (month_num % 12) + 1
    
    return render_template('business_plan/view.html', 
                          plan=plan,
                          root_items=root_items,
                          months=months)

@business_plan_bp.route('/create', methods=['POST'])
@login_required
def create_plan():
    """事業計画の新規作成"""
    data = request.form
    
    # 新しい事業計画を作成
    new_plan = BusinessPlan(
        name=data.get('name'),
        plan_type=data.get('plan_type'),
        fiscal_year=int(data.get('fiscal_year')),
        start_month=int(data.get('start_month')),
        end_month=int(data.get('end_month'))
    )
    
    db.session.add(new_plan)
    db.session.commit()
    
    # 初期項目（テンプレート）を追加
    create_default_plan_items(new_plan.id)
    
    # plan_typeに応じてリダイレクト
    if new_plan.plan_type == 'current':
        return redirect(url_for('business_plan.current_plan'))
    else:
        return redirect(url_for('business_plan.next_plan'))

@business_plan_bp.route('/item/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    """事業計画項目の取得"""
    item = PlanItem.query.get_or_404(item_id)
    
    # 項目の詳細情報をJSON形式で返す
    item_data = {
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'item_type': item.item_type,
        'description': item.description,
        'parent_id': item.parent_id,
        'quantity': item.quantity,
        'unit_price': item.unit_price,
        'unit': item.unit,
        'monthly_amounts': {
            'm1': item.m1_amount,
            'm2': item.m2_amount,
            'm3': item.m3_amount,
            'm4': item.m4_amount,
            'm5': item.m5_amount,
            'm6': item.m6_amount,
            'm7': item.m7_amount,
            'm8': item.m8_amount,
            'm9': item.m9_amount,
            'm10': item.m10_amount,
            'm11': item.m11_amount,
            'm12': item.m12_amount,
        },
        'total': item.total_amount
    }
    
    return jsonify(item_data)

@business_plan_bp.route('/item', methods=['POST'])
@login_required
def create_item():
    """事業計画項目の新規作成"""
    data = request.json
    
    new_item = PlanItem(
        business_plan_id=data.get('business_plan_id'),
        parent_id=data.get('parent_id'),
        category=data.get('category'),
        item_type=data.get('item_type', 'detail'),
        name=data.get('name'),
        description=data.get('description', ''),
        sort_order=data.get('sort_order', 0),
        quantity=data.get('quantity'),
        unit_price=data.get('unit_price'),
        unit=data.get('unit')
    )
    
    # 月別金額があれば設定
    monthly = data.get('monthly_amounts', {})
    if 'm1' in monthly: new_item.m1_amount = monthly['m1']
    if 'm2' in monthly: new_item.m2_amount = monthly['m2']
    if 'm3' in monthly: new_item.m3_amount = monthly['m3']
    if 'm4' in monthly: new_item.m4_amount = monthly['m4']
    if 'm5' in monthly: new_item.m5_amount = monthly['m5']
    if 'm6' in monthly: new_item.m6_amount = monthly['m6']
    if 'm7' in monthly: new_item.m7_amount = monthly['m7']
    if 'm8' in monthly: new_item.m8_amount = monthly['m8']
    if 'm9' in monthly: new_item.m9_amount = monthly['m9']
    if 'm10' in monthly: new_item.m10_amount = monthly['m10']
    if 'm11' in monthly: new_item.m11_amount = monthly['m11']
    if 'm12' in monthly: new_item.m12_amount = monthly['m12']
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({'id': new_item.id, 'success': True})

@business_plan_bp.route('/item/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """事業計画項目の更新"""
    item = PlanItem.query.get_or_404(item_id)
    data = request.json
    
    # 基本情報の更新
    if 'name' in data: item.name = data['name']
    if 'category' in data: item.category = data['category']
    if 'description' in data: item.description = data['description']
    if 'quantity' in data: item.quantity = data['quantity']
    if 'unit_price' in data: item.unit_price = data['unit_price']
    if 'unit' in data: item.unit = data['unit']
    
    # 月別金額の更新
    monthly = data.get('monthly_amounts', {})
    if 'm1' in monthly: item.m1_amount = monthly['m1']
    if 'm2' in monthly: item.m2_amount = monthly['m2']
    if 'm3' in monthly: item.m3_amount = monthly['m3']
    if 'm4' in monthly: item.m4_amount = monthly['m4']
    if 'm5' in monthly: item.m5_amount = monthly['m5']
    if 'm6' in monthly: item.m6_amount = monthly['m6']
    if 'm7' in monthly: item.m7_amount = monthly['m7']
    if 'm8' in monthly: item.m8_amount = monthly['m8']
    if 'm9' in monthly: item.m9_amount = monthly['m9']
    if 'm10' in monthly: item.m10_amount = monthly['m10']
    if 'm11' in monthly: item.m11_amount = monthly['m11']
    if 'm12' in monthly: item.m12_amount = monthly['m12']
    
    db.session.commit()
    
    return jsonify({'success': True})

@business_plan_bp.route('/item/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """事業計画項目の削除"""
    item = PlanItem.query.get_or_404(item_id)
    
    # 子項目も一緒に削除（SQLAlchemyのカスケード設定があるためDB上では自動的に削除される）
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'success': True})

def create_default_plan_items(business_plan_id):
    """新規事業計画の初期項目を作成する補助関数"""
    # 親項目の作成
    root_categories = [
        {'name': '売上高', 'category': '売上', 'item_type': 'header', 'sort_order': 10},
        {'name': '売上原価', 'category': '原価', 'item_type': 'header', 'sort_order': 20},
        {'name': '売上総利益', 'category': '売上総利益', 'item_type': 'header', 'sort_order': 30},
        {'name': '販売費および一般管理費', 'category': '販管費', 'item_type': 'header', 'sort_order': 40},
        {'name': '営業利益', 'category': '営業利益', 'item_type': 'header', 'sort_order': 50},
        {'name': '営業外収益', 'category': '営業外収益', 'item_type': 'header', 'sort_order': 60},
        {'name': '営業外費用', 'category': '営業外費用', 'item_type': 'header', 'sort_order': 70},
        {'name': '経常利益', 'category': '経常利益', 'item_type': 'header', 'sort_order': 80},
        {'name': '特別利益', 'category': '特別利益', 'item_type': 'header', 'sort_order': 90},
        {'name': '特別損失', 'category': '特別損失', 'item_type': 'header', 'sort_order': 100},
        {'name': '税引前当期純利益', 'category': '税引前利益', 'item_type': 'header', 'sort_order': 110},
        {'name': '法人税等', 'category': '法人税等', 'item_type': 'header', 'sort_order': 120},
        {'name': '当期純利益', 'category': '当期純利益', 'item_type': 'header', 'sort_order': 130},
    ]
    
    # 親項目のIDマップ（子項目作成のため）
    parent_id_map = {}
    
    # 親項目の作成
    for category_data in root_categories:
        item = PlanItem(
            business_plan_id=business_plan_id,
            parent_id=None,
            **category_data
        )
        db.session.add(item)
        db.session.flush()  # IDを取得するためフラッシュ
        parent_id_map[category_data['category']] = item.id
    
    # サンプル子項目の作成
    child_items = [
        {
            'parent_category': '売上',
            'name': '商品A', 
            'category': '売上', 
            'item_type': 'detail',
            'sort_order': 1
        },
        {
            'parent_category': '原価',
            'name': '商品A原価', 
            'category': '原価', 
            'item_type': 'detail',
            'sort_order': 1
        },
        {
            'parent_category': '販管費',
            'name': '人件費', 
            'category': '販管費', 
            'item_type': 'detail',
            'sort_order': 1
        },
        {
            'parent_category': '販管費',
            'name': '賃借料', 
            'category': '販管費', 
            'item_type': 'detail',
            'sort_order': 2
        },
    ]
    
    # 子項目の作成
    for child_data in child_items:
        parent_category = child_data.pop('parent_category')
        parent_id = parent_id_map.get(parent_category)
        
        if parent_id:
            item = PlanItem(
                business_plan_id=business_plan_id,
                parent_id=parent_id,
                **child_data
            )
            db.session.add(item)
    
    db.session.commit() 