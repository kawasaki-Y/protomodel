from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.business import RevenueBusiness, Service, Customer
from app.models.revenue_plan import RevenuePlan, RevenuePlanDetail

bp = Blueprint('business', __name__, url_prefix='/api/business')

@bp.route('/businesses', methods=['GET'])
@login_required
def get_businesses():
    """事業一覧を取得するAPI"""
    try:
        businesses = RevenueBusiness.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'success': True,
            'businesses': [
                {
                    'id': business.id,
                    'name': business.name,
                    'description': business.description
                }
                for business in businesses
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'事業の取得に失敗しました: {str(e)}'})

@bp.route('/businesses', methods=['POST'])
@login_required
def create_business():
    """新規事業を登録するAPI"""
    data = request.form
    
    # 必須項目のバリデーション
    if not data.get('business_name'):
        return jsonify({'success': False, 'message': '事業名は必須です'})
    
    # 事業の作成
    try:
        business = RevenueBusiness(
            name=data.get('business_name'),
            description=data.get('business_description', ''),
            user_id=current_user.id
        )
        
        db.session.add(business)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '事業を登録しました',
            'business': {
                'id': business.id,
                'name': business.name,
                'description': business.description
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'事業の登録に失敗しました: {str(e)}'})

@bp.route('/services', methods=['GET'])
@login_required
def get_services():
    """サービス一覧を取得するAPI"""
    try:
        services = Service.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'success': True,
            'services': [
                {
                    'id': service.id,
                    'service_name': service.service_name,
                    'default_price': service.default_price,
                    'description': service.description
                }
                for service in services
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'サービスの取得に失敗しました: {str(e)}'})

@bp.route('/services', methods=['POST'])
@login_required
def create_service():
    """新規サービスを登録するAPI"""
    data = request.form
    
    # 必須項目のバリデーション
    if not data.get('service_name'):
        return jsonify({'success': False, 'message': 'サービス名は必須です'})
    
    if not data.get('default_price'):
        return jsonify({'success': False, 'message': '標準単価は必須です'})
    
    # サービスの作成
    try:
        service = Service(
            service_name=data.get('service_name'),
            default_price=int(data.get('default_price', 0)),
            description=data.get('service_description', ''),
            user_id=current_user.id
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'サービスを登録しました',
            'service': {
                'id': service.id,
                'service_name': service.service_name,
                'default_price': service.default_price,
                'description': service.description
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'サービスの登録に失敗しました: {str(e)}'})

@bp.route('/customers', methods=['GET'])
@login_required
def get_customers():
    """顧客一覧を取得するAPI"""
    try:
        customers = Customer.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'success': True,
            'customers': [
                {
                    'id': customer.id,
                    'customer_name': customer.customer_name,
                    'default_price': customer.default_price,
                    'description': customer.description
                }
                for customer in customers
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'顧客の取得に失敗しました: {str(e)}'})

@bp.route('/customers', methods=['POST'])
@login_required
def create_customer():
    """新規顧客を登録するAPI"""
    data = request.form
    
    # 必須項目のバリデーション
    if not data.get('customer_name'):
        return jsonify({'success': False, 'message': '顧客名は必須です'})
    
    # 顧客の作成
    try:
        customer = Customer(
            customer_name=data.get('customer_name'),
            default_price=int(data.get('default_price', 0)) if data.get('default_price') else None,
            description=data.get('customer_description', ''),
            user_id=current_user.id
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '顧客を登録しました',
            'customer': {
                'id': customer.id,
                'customer_name': customer.customer_name,
                'default_price': customer.default_price,
                'description': customer.description
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'顧客の登録に失敗しました: {str(e)}'}) 