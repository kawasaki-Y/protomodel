from flask import Blueprint, render_template, jsonify, redirect, url_for, current_app, abort, flash, request
from app.models.models import db, BusinessPlan, BusinessPlanItem, CashFlowPlan, CashFlowItem
from flask_login import login_required, current_user
from app.models.business import RevenueBusiness, Service, Customer
from app.models.sales_record import SalesRecord
from datetime import datetime, timedelta
import random
from flask import session

# Blueprintの定義
bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@bp.route('/home')
def home():
    """ホーム画面（未ログイン時のランディングページ）"""
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """ダッシュボード画面"""
    # KPIデータの取得
    kpi_data = {
        'revenue': {
            'title': '売上高',
            'value': calculate_total_revenue(),
            'unit': '円',
            'progress': calculate_revenue_progress(),
            'url': url_for('main.revenue_plan')
        },
        'profit': {
            'title': '営業利益',
            'value': calculate_total_profit(),
            'unit': '円',
            'progress': calculate_profit_progress(),
            'url': '#'
        },
        'cash': {
            'title': '資金残高',
            'value': get_current_cash_balance(),
            'unit': '円',
            'url': '#'
        }
    }
    
    return render_template('dashboard.html', 
                         kpi_data=kpi_data,
                         page_title='ダッシュボード')

def get_recent_activities():
    """最近の活動を取得"""
    # 実際のアプリケーションでは、活動ログのデータベースから取得
    return [
        {'description': '新しい収益モデルを作成しました', 'created_at': datetime.now()},
        {'description': '月次売上データを更新しました', 'created_at': datetime.now() - timedelta(days=1)},
        {'description': '事業計画を更新しました', 'created_at': datetime.now() - timedelta(days=2)},
    ]

@bp.route('/settings')
@login_required
def settings():
    """
    設定画面
    
    ユーザー設定や事業計画の基本設定を管理
    """
    return render_template('main/settings.html')

@bp.route('/api/dashboard/chart-data')
@login_required
def get_dashboard_chart_data():
    """ダッシュボード用のチャートデータを提供するAPI"""
    # 既存のコードを維持
    return jsonify({
        'labels': ['1月', '2月', '3月', '4月', '5月', '6月'],
        'sales': [8500000, 9200000, 8700000, 10300000, 9800000, 11200000],
        'profit': [2300000, 2500000, 2100000, 2800000, 2600000, 3100000]
    })

# KPI計算用のヘルパー関数
def calculate_total_revenue():
    # 実際のデータベースから計算する（実装予定）
    return 10000000

def calculate_revenue_progress():
    # 実際のデータベースから計算する（実装予定）
    return 75

def calculate_total_profit():
    # 実際のデータベースから計算する（実装予定）
    return 3000000

def calculate_profit_progress():
    # 実際のデータベースから計算する（実装予定）
    return 80

def get_current_cash_balance():
    # 実際のデータベースから取得する（実装予定）
    return 15000000

@bp.route('/debug-session')
def debug_session():
    """デバッグ用：現在のセッション情報を表示する"""
    if current_app.debug:
        from flask_login import current_user
        
        session_data = {
            'session_keys': list(session.keys()),
            'user_id': session.get('_user_id'),
            'is_authenticated': current_user.is_authenticated if current_user else False,
            'current_user_info': {
                'id': current_user.id,
                'email': current_user.email
            } if current_user and current_user.is_authenticated else None
        }
        
        return jsonify(session_data)
    
    # 本番環境では404を返す
    abort(404)

@bp.route('/business/setting', methods=['GET', 'POST'])
@login_required
def business_setting():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            
            if not name:
                flash('事業名を入力してください。', 'error')
                return redirect(url_for('main.business_setting'))

            # トランザクションを明示的に開始
            business = RevenueBusiness(
                name=name,
                user_id=current_user.id
            )
            
            try:
                db.session.add(business)
                db.session.commit()
                flash('事業を登録しました。', 'success')
            except Exception as db_error:
                db.session.rollback()
                current_app.logger.error(f"DB操作エラー: {str(db_error)}")
                flash('事業の登録に失敗しました。', 'error')

            return redirect(url_for('main.business_setting'))

        except Exception as e:
            current_app.logger.error(f"事業登録中にエラー: {str(e)}")
            flash('事業の登録に失敗しました。', 'error')
            return redirect(url_for('main.business_setting'))

    # GET リクエストの場合
    businesses = RevenueBusiness.query.filter_by(user_id=current_user.id).all()
    return render_template('business/setting.html', businesses=businesses)

@bp.route('/service/setting', methods=['GET', 'POST'])
@login_required
def service_setting():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            
            if not name:
                flash('サービス名を入力してください。', 'error')
                return redirect(url_for('main.service_setting'))

            service = Service(
                name=name,
                # 他のフィールドはデフォルト値または空値を使用
                price=0,  # デフォルト値として0を設定
                business_id=1  # デフォルトの事業IDを設定
            )
            
            db.session.add(service)
            db.session.commit()

            flash('サービスを登録しました。', 'success')
            return redirect(url_for('main.service_setting'))

        except Exception as e:
            db.session.rollback()
            flash('サービスの登録に失敗しました。', 'error')
            return redirect(url_for('main.service_setting'))

    # GET リクエストの場合
    services = Service.query.all()
    return render_template('business/service_setting.html', services=services)

@bp.route('/customer/setting', methods=['GET', 'POST'])
@login_required
def customer_setting():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            
            if not name:
                flash('顧客名を入力してください。', 'error')
                return redirect(url_for('main.customer_setting'))

            customer = Customer(
                name=name,
                price_factor=1.0,  # デフォルト値
                business_id=1  # デフォルト値
            )
            
            db.session.add(customer)
            db.session.commit()

            flash('顧客を登録しました。', 'success')
            return redirect(url_for('main.customer_setting'))

        except Exception as e:
            db.session.rollback()
            flash('顧客の登録に失敗しました。', 'error')
            return redirect(url_for('main.customer_setting'))

    # GET リクエストの場合
    customers = Customer.query.all()
    return render_template('business/customer_setting.html', customers=customers)

@bp.route('/revenue-plan')
@login_required
def revenue_plan():
    """収益計画ページ"""
    return render_template('business/revenue_plan.html')

@bp.route('/api/revenue-plan/<int:business_id>', methods=['GET'])
@login_required
def get_revenue_plan(business_id):
    try:
        business = RevenueBusiness.query.get_or_404(business_id)
        # 現在のユーザーの事業かチェック
        if business.user_id != current_user.id:
            abort(403)
            
        customers = Customer.query.filter_by(business_id=business_id).all()
        services = Service.query.filter_by(business_id=business_id).all()
        
        # 収益計画データの取得
        values = {}
        plan_values = RevenuePlanValue.query.filter_by(business_id=business_id).all()
        
        for value in plan_values:
            if value.customer_id not in values:
                values[value.customer_id] = {}
            if value.service_id not in values[value.customer_id]:
                values[value.customer_id][value.service_id] = {}
            values[value.customer_id][value.service_id][value.month] = value.value
        
        return jsonify({
            'business': {
                'id': business.id,
                'name': business.name
            },
            'customers': [{
                'id': c.id,
                'name': c.name,
                'price_factor': c.price_factor
            } for c in customers],
            'services': [{
                'id': s.id,
                'name': s.name,
                'price': s.price
            } for s in services],
            'values': values
        })
    except Exception as e:
        current_app.logger.error(f"収益計画の取得中にエラーが発生: {str(e)}")
        return jsonify({'error': 'データの取得に失敗しました'}), 500

@bp.route('/api/revenue-plan', methods=['POST'])
@login_required
def save_revenue_plan():
    try:
        data = request.get_json()
        business_id = data.get('business_id')
        values = data.get('values', {})
        
        # 事業所有者チェック
        business = RevenueBusiness.query.get_or_404(business_id)
        if business.user_id != current_user.id:
            abort(403)
        
        # 既存のデータを一旦削除
        RevenuePlanValue.query.filter_by(business_id=business_id).delete()
        
        # 新しいデータを保存
        for customer_id, services in values.items():
            for service_id, months in services.items():
                for month, value in months.items():
                    plan_value = RevenuePlanValue(
                        business_id=business_id,
                        customer_id=int(customer_id),
                        service_id=int(service_id),
                        month=int(month),
                        value=float(value)
                    )
                    db.session.add(plan_value)
        
        db.session.commit()
        return jsonify({'status': 'success'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"収益計画の保存中にエラーが発生: {str(e)}")
        return jsonify({'error': 'データの保存に失敗しました'}), 500

@bp.route('/api/revenue-plan/delete-row', methods=['POST'])
@login_required
def delete_revenue_plan_row():
    try:
        data = request.get_json()
        business_id = data.get('business_id')
        customer_id = data.get('customer_id')
        service_id = data.get('service_id')
        
        # 事業所有者チェック
        business = RevenueBusiness.query.get_or_404(business_id)
        if business.user_id != current_user.id:
            abort(403)
        
        # 指定された行のデータを削除
        RevenuePlanValue.query.filter_by(
            business_id=business_id,
            customer_id=customer_id,
            service_id=service_id
        ).delete()
        
        db.session.commit()
        return jsonify({'status': 'success'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"収益計画の行削除中にエラーが発生: {str(e)}")
        return jsonify({'error': '行の削除に失敗しました'}), 500 