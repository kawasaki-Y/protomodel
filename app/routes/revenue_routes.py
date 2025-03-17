from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.models import db, BusinessPlan, RevenueBusinessModel

revenue_bp = Blueprint('revenue', __name__, url_prefix='/revenue')

@revenue_bp.route('/')
@login_required
def index():
    """収益事業一覧を表示"""
    return render_template('revenue/index.html')

@revenue_bp.route('/create', methods=['GET'])
@login_required
def create():
    """新規収益事業の作成フォームを表示"""
    business_types = [
        {'id': 'unit_sales', 'name': '単価×数量'},
        {'id': 'subscription', 'name': 'サブスクリプション'},
        {'id': 'project', 'name': 'プロジェクト'},
        {'id': 'service', 'name': 'サービス'},
    ]
    return render_template('revenue/create.html', business_types=business_types)

@revenue_bp.route('/api/revenue-models', methods=['GET'])
@login_required
def get_revenue_models():
    """収益事業モデルの一覧を取得"""
    business_plan_id = request.args.get('business_plan_id')
    if not business_plan_id:
        return jsonify({'error': '事業計画IDが必要です'}), 400
        
    models = RevenueBusinessModel.query.filter_by(business_plan_id=business_plan_id).all()
    return jsonify([{
        'id': model.id,
        'name': model.name,
        'business_type': model.business_type,
        'description': model.description,
        'parameters': model.parameters,
        'total_amount': model.total_amount,
        'monthly_amounts': [model.get_month_amount(i) for i in range(1, 13)]
    } for model in models])

@revenue_bp.route('/api/revenue-models', methods=['POST'])
@login_required
def create_revenue_model():
    """新規収益事業モデルを作成"""
    data = request.get_json()
    
    # 必須フィールドの検証
    required_fields = ['business_plan_id', 'name', 'business_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': '必須フィールドが不足しています'}), 400
    
    # 新規モデルの作成
    model = RevenueBusinessModel(
        business_plan_id=data['business_plan_id'],
        name=data['name'],
        business_type=data['business_type'],
        description=data.get('description', ''),
        parameters=data.get('parameters', {})
    )
    
    # パラメータに基づいて月別売上を計算
    model.calculate_monthly_revenue()
    
    # データベースに保存
    db.session.add(model)
    db.session.commit()
    
    return jsonify({
        'id': model.id,
        'name': model.name,
        'business_type': model.business_type,
        'description': model.description,
        'parameters': model.parameters,
        'total_amount': model.total_amount,
        'monthly_amounts': [model.get_month_amount(i) for i in range(1, 13)]
    }), 201

@revenue_bp.route('/api/revenue-models/<int:model_id>', methods=['PUT'])
@login_required
def update_revenue_model(model_id):
    """収益事業モデルを更新"""
    model = RevenueBusinessModel.query.get_or_404(model_id)
    data = request.get_json()
    
    # フィールドの更新
    if 'name' in data:
        model.name = data['name']
    if 'business_type' in data:
        model.business_type = data['business_type']
    if 'description' in data:
        model.description = data['description']
    if 'parameters' in data:
        model.parameters = data['parameters']
        model.calculate_monthly_revenue()
    
    db.session.commit()
    
    return jsonify({
        'id': model.id,
        'name': model.name,
        'business_type': model.business_type,
        'description': model.description,
        'parameters': model.parameters,
        'total_amount': model.total_amount,
        'monthly_amounts': [model.get_month_amount(i) for i in range(1, 13)]
    })

@revenue_bp.route('/api/revenue-models/<int:model_id>', methods=['DELETE'])
@login_required
def delete_revenue_model(model_id):
    """収益事業モデルを削除"""
    model = RevenueBusinessModel.query.get_or_404(model_id)
    db.session.delete(model)
    db.session.commit()
    return '', 204 