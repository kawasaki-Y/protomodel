from flask import Blueprint, render_template, jsonify, redirect, url_for, current_app, abort
from app.models.models import db, BusinessPlan, BusinessPlanItem, CashFlowPlan, CashFlowItem
from flask_login import login_required, current_user
from app.models.business import RevenueBusiness
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

@bp.route('/business-setting')
@login_required
def business_setting():
    """事業設定ページ"""
    return render_template('business/business_setting.html')

@bp.route('/service-setting')
@login_required
def service_setting():
    """サービス設定ページ"""
    return render_template('business/service_setting.html')

@bp.route('/customer-setting')
@login_required
def customer_setting():
    """顧客設定ページ"""
    return render_template('business/customer_setting.html')

@bp.route('/revenue-plan')
@login_required
def revenue_plan():
    """収益計画ページ"""
    return render_template('business/revenue_plan.html') 