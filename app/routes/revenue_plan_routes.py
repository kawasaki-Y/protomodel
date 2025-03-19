from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.revenue_model import Business, Product, Market, RevenuePlan, RevenueDetail
from app.models.user import User
from datetime import datetime
import calendar
import json

revenue_plan_bp = Blueprint('revenue_plan', __name__, url_prefix='/revenue-plan')

@revenue_plan_bp.route('/')
@login_required
def index():
    """収益計画のメインページ"""
    return render_template('revenue_plan/index.html')

@revenue_plan_bp.route('/business-settings', methods=['GET'])
@login_required
def business_settings():
    """事業設定タブ"""
    return render_template('revenue_plan/business_settings.html')

@revenue_plan_bp.route('/revenue-input', methods=['GET'])
@login_required
def revenue_input():
    """売上計画入力タブ"""
    return render_template('revenue_plan/revenue_input.html')

@revenue_plan_bp.route('/business')
@login_required
def business_tab():
    """事業設定タブ"""
    businesses = Business.query.filter_by(user_id=current_user.id).all()
    return render_template('revenue_plan/business_tab.html', businesses=businesses)

@revenue_plan_bp.route('/planning')
@login_required
def planning_tab():
    """売上計画入力タブ"""
    # 年度とシナリオの取得
    fiscal_year = request.args.get('year', type=int, default=datetime.now().year)
    scenario = request.args.get('scenario', default='standard')
    
    # 事業一覧を取得
    businesses = Business.query.filter_by(user_id=current_user.id).all()
    
    # 各事業の商品・顧客情報を取得
    business_data = []
    for business in businesses:
        # 売上計画の取得（なければ新規作成）
        plan = RevenuePlan.query.filter_by(
            user_id=current_user.id,
            business_id=business.id,
            fiscal_year=fiscal_year,
            scenario=scenario
        ).first()
        
        if not plan:
            plan = RevenuePlan(
                user_id=current_user.id,
                business_id=business.id,
                fiscal_year=fiscal_year,
                scenario=scenario
            )
            db.session.add(plan)
            db.session.commit()
        
        # 商品・顧客情報の取得
        products = Product.query.filter_by(business_id=business.id).all()
        markets = Market.query.filter_by(business_id=business.id).all()
        
        # 月別売上データの取得
        monthly_data = {}
        details = RevenueDetail.query.filter_by(plan_id=plan.id).all()
        
        for detail in details:
            key = f"{detail.product_id}_{detail.market_id}_{detail.month}"
            monthly_data[key] = {
                'unit_price': detail.unit_price,
                'quantity': detail.quantity,
                'amount': detail.amount,
                'notes': detail.notes
            }
        
        business_data.append({
            'business': business,
            'products': products,
            'markets': markets,
            'plan': plan,
            'monthly_data': monthly_data
        })
    
    # 月名のリスト
    months = [calendar.month_name[i][0:3] for i in range(1, 13)]
    
    return render_template(
        'revenue_plan/planning_tab.html',
        business_data=business_data,
        months=months,
        fiscal_year=fiscal_year,
        scenario=scenario
    )

@revenue_plan_bp.route('/api/revenue-plan/business-settings', methods=['POST'])
@login_required
def update_business_settings():
    """事業設定の更新API"""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    data = request.get_json()
    # データ処理ロジックをここに追加
    return jsonify({"status": "success"})

@revenue_plan_bp.route('/api/business', methods=['POST'])
@login_required
def create_business():
    """事業を新規追加"""
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    
    business = Business(
        user_id=current_user.id,
        name=name,
        description=description
    )
    
    db.session.add(business)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'business': {
            'id': business.id,
            'name': business.name,
            'description': business.description
        }
    })

@revenue_plan_bp.route('/api/business/<int:business_id>', methods=['PUT'])
@login_required
def update_business(business_id):
    """事業情報を更新"""
    business = Business.query.filter_by(id=business_id, user_id=current_user.id).first_or_404()
    data = request.json
    
    business.name = data.get('name', business.name)
    business.description = data.get('description', business.description)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'business': {
            'id': business.id,
            'name': business.name,
            'description': business.description
        }
    })

@revenue_plan_bp.route('/api/business/<int:business_id>', methods=['DELETE'])
@login_required
def delete_business(business_id):
    """事業を削除"""
    business = Business.query.filter_by(id=business_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(business)
    db.session.commit()
    
    return jsonify({'success': True})

@revenue_plan_bp.route('/api/business/<int:business_id>/product', methods=['POST'])
@login_required
def create_product(business_id):
    """商品を新規追加"""
    business = Business.query.filter_by(id=business_id, user_id=current_user.id).first_or_404()
    data = request.json
    
    product = Product(
        business_id=business.id,
        name=data.get('name'),
        description=data.get('description', ''),
        unit_price=data.get('unit_price', 0),
        price_unit=data.get('price_unit', '')
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'product': {
            'id': product.id,
            'name': product.name,
            'unit_price': product.unit_price,
            'price_unit': product.price_unit
        }
    })

@revenue_plan_bp.route('/api/product/<int:product_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_product(product_id):
    """商品の更新・削除"""
    product = Product.query.join(Business).filter(
        Product.id == product_id,
        Business.user_id == current_user.id
    ).first_or_404()
    
    if request.method == 'DELETE':
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True})
    
    # PUT の場合
    data = request.json
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.unit_price = data.get('unit_price', product.unit_price)
    product.price_unit = data.get('price_unit', product.price_unit)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'product': {
            'id': product.id,
            'name': product.name,
            'unit_price': product.unit_price
        }
    })

@revenue_plan_bp.route('/api/business/<int:business_id>/market', methods=['POST'])
@login_required
def create_market(business_id):
    """顧客・市場を新規追加"""
    business = Business.query.filter_by(id=business_id, user_id=current_user.id).first_or_404()
    data = request.json
    
    market = Market(
        business_id=business.id,
        name=data.get('name'),
        description=data.get('description', '')
    )
    
    db.session.add(market)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'market': {
            'id': market.id,
            'name': market.name
        }
    })

@revenue_plan_bp.route('/api/market/<int:market_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_market(market_id):
    """顧客・市場の更新・削除"""
    market = Market.query.join(Business).filter(
        Market.id == market_id,
        Business.user_id == current_user.id
    ).first_or_404()
    
    if request.method == 'DELETE':
        db.session.delete(market)
        db.session.commit()
        return jsonify({'success': True})
    
    # PUT の場合
    data = request.json
    market.name = data.get('name', market.name)
    market.description = data.get('description', market.description)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'market': {
            'id': market.id,
            'name': market.name
        }
    })

@revenue_plan_bp.route('/api/revenue', methods=['POST'])
@login_required
def save_revenue_detail():
    """売上詳細データの保存"""
    data = request.json
    plan_id = data.get('plan_id')
    product_id = data.get('product_id')
    market_id = data.get('market_id')
    month = data.get('month')
    unit_price = data.get('unit_price', 0)
    quantity = data.get('quantity', 0)
    amount = data.get('amount')
    notes = data.get('notes', '')
    
    # 権限チェック
    plan = RevenuePlan.query.filter_by(id=plan_id).first_or_404()
    if plan.user_id != current_user.id:
        return jsonify({'success': False, 'message': '権限がありません'})
    
    # 既存レコードの検索
    detail = RevenueDetail.query.filter_by(
        plan_id=plan_id,
        product_id=product_id,
        market_id=market_id,
        month=month
    ).first()
    
    # 既存レコードの更新または新規作成
    if detail:
        detail.unit_price = unit_price
        detail.quantity = quantity
        detail.amount = amount if amount is not None else unit_price * quantity
        detail.notes = notes
    else:
        detail = RevenueDetail(
            plan_id=plan_id,
            product_id=product_id,
            market_id=market_id,
            month=month,
            unit_price=unit_price,
            quantity=quantity,
            amount=amount if amount is not None else unit_price * quantity,
            notes=notes
        )
        db.session.add(detail)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'detail': {
            'id': detail.id,
            'amount': detail.amount
        }
    })

@revenue_plan_bp.route('/api/plan-summary/<int:fiscal_year>/<string:scenario>')
@login_required
def get_plan_summary(fiscal_year, scenario):
    """売上計画の年間サマリーを取得"""
    plans = RevenuePlan.query.filter_by(
        user_id=current_user.id,
        fiscal_year=fiscal_year,
        scenario=scenario
    ).all()
    
    total_revenue = 0
    business_totals = []
    monthly_totals = [0] * 12
    
    for plan in plans:
        business_total = 0
        business_monthly = [0] * 12
        
        details = RevenueDetail.query.filter_by(plan_id=plan.id).all()
        for detail in details:
            business_monthly[detail.month - 1] += detail.amount
            business_total += detail.amount
            monthly_totals[detail.month - 1] += detail.amount
        
        total_revenue += business_total
        
        business_totals.append({
            'business_id': plan.business_id,
            'business_name': plan.business.name,
            'total': business_total,
            'monthly': business_monthly
        })
    
    return jsonify({
        'success': True,
        'total_revenue': total_revenue,
        'business_totals': business_totals,
        'monthly_totals': monthly_totals
    })

@revenue_plan_bp.route('/scenario-comparison')
@login_required
def scenario_comparison():
    """シナリオ比較ページを表示します"""
    return render_template('revenue_plan/scenario_comparison.html')

@revenue_plan_bp.route('/import-export')
@login_required
def import_export():
    """データのインポート/エクスポートページを表示します"""
    return render_template('revenue_plan/import_export.html') 