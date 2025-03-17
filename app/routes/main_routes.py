from flask import Blueprint, render_template, jsonify, redirect, url_for
from app.models.models import db, BusinessPlan, BusinessPlanItem, CashFlowPlan, CashFlowItem
from flask_login import login_required, current_user
from app.models.revenue_business import RevenueBusiness
from app.models.sales_record import SalesRecord

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    トップページ
    
    未ログインユーザー向けのランディングページを表示
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/home')
def home():
    """ホーム画面（未ログイン時のランディングページ）"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    ダッシュボード
    
    ユーザーの事業計画の概要と主要な指標を表示
    - 収益事業モデルの一覧
    - 月次売上の推移
    - 重要なKPI
    """
    # 収益事業モデルの取得
    revenue_businesses = RevenueBusiness.query.filter_by(user_id=current_user.id).all()
    
    # 売上データの集計
    sales_summary = {}
    for business in revenue_businesses:
        records = SalesRecord.query.filter_by(revenue_business_id=business.id).all()
        sales_summary[business.id] = {
            'name': business.name,
            'total_sales': sum(record.total_amount for record in records),
            'records': records
        }
    
    return render_template('main/dashboard.html',
                         revenue_businesses=revenue_businesses,
                         sales_summary=sales_summary)

@main_bp.route('/settings')
@login_required
def settings():
    """
    設定画面
    
    ユーザー設定や事業計画の基本設定を管理
    """
    return render_template('main/settings.html')

@main_bp.route('/api/dashboard/chart-data')
@login_required
def get_dashboard_chart_data():
    """ダッシュボード用のチャートデータを返すAPI"""
    # ビジネスプランを取得
    business_plan = BusinessPlan.query.filter_by(user_id=current_user.id).first()
    
    if not business_plan:
        # データがない場合はサンプルデータを返す
        return jsonify({
            'sales': generate_sample_sales_data(),
            'profit': generate_sample_profit_data(),
            'exists': False
        })
    
    # 売上項目と利益項目を取得
    sales_items = BusinessPlanItem.query.filter_by(
        business_plan_id=business_plan.id,
        category='収益'
    ).all()
    
    expense_items = BusinessPlanItem.query.filter_by(
        business_plan_id=business_plan.id,
        category='費用'
    ).all()
    
    # 月ごとの売上と費用を集計
    monthly_sales = [0] * 12
    monthly_expenses = [0] * 12
    
    for item in sales_items:
        for month in range(1, 13):
            monthly_sales[month-1] += item.get_month_amount(month)
    
    for item in expense_items:
        for month in range(1, 13):
            monthly_expenses[month-1] += item.get_month_amount(month)
    
    # 利益を計算
    monthly_profit = [s - e for s, e in zip(monthly_sales, monthly_expenses)]
    
    # 月ラベルを取得
    if hasattr(business_plan, 'months') and business_plan.months:
        month_labels = business_plan.months
    else:
        # 暫定：1月から12月
        month_labels = [f"{business_plan.year}-{m:02d}" for m in range(1, 13)]
    
    return jsonify({
        'labels': month_labels,
        'sales': monthly_sales,
        'profit': monthly_profit,
        'exists': True
    })

def generate_sample_sales_data():
    """サンプルの売上データを生成"""
    return [1200000, 1300000, 1400000, 1450000, 1500000, 
            1550000, 1600000, 1650000, 1700000, 1750000, 
            1800000, 1850000]

def generate_sample_profit_data():
    """サンプルの利益データを生成"""
    return [240000, 260000, 280000, 290000, 300000, 
            310000, 320000, 330000, 340000, 350000, 
            360000, 370000] 