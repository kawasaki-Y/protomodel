from flask import Blueprint, render_template, jsonify, redirect, url_for
from app.models.models import db, BusinessPlan, BusinessPlanItem, CashFlowPlan, CashFlowItem
from flask_login import login_required, current_user
from app.models.revenue_business import RevenueBusiness
from app.models.sales_record import SalesRecord
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    トップページ
    
    ログイン済みの場合はダッシュボードへ、
    未ログインの場合はログイン画面へリダイレクト
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/home')
def home():
    """ホーム画面（未ログイン時のランディングページ）"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    ダッシュボードページ
    Apple風のモダンなデザインで各種データを表示
    """
    try:
        # 収益事業モデルの取得
        revenue_businesses = RevenueBusiness.query.filter_by(user_id=current_user.id).all()
        
        # 売上データの集計
        monthly_sales = [0] * 12
        total_monthly_sales = 0
        revenue_composition = {}
        
        for business in revenue_businesses:
            records = SalesRecord.query.filter_by(revenue_business_id=business.id).all()
            business_total = sum(record.total_amount for record in records)
            revenue_composition[business.name] = business_total
            
            for record in records:
                month = record.month.month - 1
                monthly_sales[month] += record.total_amount
                if month == datetime.now().month - 1:
                    total_monthly_sales += record.total_amount

        # 前月比成長率の計算
        current_month = datetime.now().month - 1
        if current_month > 0 and monthly_sales[current_month - 1] > 0:
            sales_growth = ((monthly_sales[current_month] - monthly_sales[current_month - 1]) / 
                          monthly_sales[current_month - 1] * 100)
        else:
            sales_growth = 0

        # 収益構成データの準備
        revenue_composition_labels = list(revenue_composition.keys())
        revenue_composition_data = list(revenue_composition.values())

        # 目標達成率の計算（仮の目標値）
        target_sales = 10000000  # 1000万円
        achievement_rate = min(int((total_monthly_sales / target_sales) * 100), 100)

        return render_template('main/dashboard.html',
                            revenue_businesses=revenue_businesses,
                            total_monthly_sales=total_monthly_sales,
                            sales_growth=round(sales_growth, 1),
                            monthly_sales=monthly_sales,
                            achievement_rate=achievement_rate,
                            revenue_composition_labels=revenue_composition_labels,
                            revenue_composition_data=revenue_composition_data,
                            recent_activities=get_recent_activities())
                            
    except Exception as e:
        return render_template('main/dashboard.html',
                            revenue_businesses=[],
                            total_monthly_sales=0,
                            sales_growth=0,
                            monthly_sales=[0] * 12,
                            achievement_rate=0,
                            revenue_composition_labels=[],
                            revenue_composition_data=[],
                            recent_activities=[],
                            error=str(e))

def get_recent_activities():
    """最近の活動を取得"""
    # 実際のアプリケーションでは、活動ログのデータベースから取得
    return [
        {'description': '新しい収益モデルを作成しました', 'created_at': datetime.now()},
        {'description': '月次売上データを更新しました', 'created_at': datetime.now() - timedelta(days=1)},
        {'description': '事業計画を更新しました', 'created_at': datetime.now() - timedelta(days=2)},
    ]

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
    """
    ダッシュボード用のチャートデータを提供するAPI
    
    返却データ：
    - 月別の売上推移
    - 月別の利益推移
    - 月ラベル
    """
    business_plan = BusinessPlan.query.filter_by(user_id=current_user.id).first()
    
    if not business_plan:
        return jsonify({
            'sales': generate_sample_sales_data(),
            'profit': generate_sample_profit_data(),
            'exists': False
        })
    
    # 売上・費用項目の取得と集計
    sales_items = BusinessPlanItem.query.filter_by(
        business_plan_id=business_plan.id,
        category='収益'
    ).all()
    
    expense_items = BusinessPlanItem.query.filter_by(
        business_plan_id=business_plan.id,
        category='費用'
    ).all()
    
    # 月次データの集計
    monthly_sales = [0] * 12
    monthly_expenses = [0] * 12
    
    for item in sales_items:
        for month in range(1, 13):
            monthly_sales[month-1] += item.get_month_amount(month)
    
    for item in expense_items:
        for month in range(1, 13):
            monthly_expenses[month-1] += item.get_month_amount(month)
    
    monthly_profit = [s - e for s, e in zip(monthly_sales, monthly_expenses)]
    
    # 月ラベルの生成
    month_labels = [f"{business_plan.year}-{m:02d}" for m in range(1, 13)]
    
    return jsonify({
        'labels': month_labels,
        'sales': monthly_sales,
        'profit': monthly_profit,
        'exists': True
    })

def generate_sample_sales_data():
    """サンプルの売上データを生成（データが存在しない場合用）"""
    return [1200000, 1300000, 1400000, 1450000, 1500000, 
            1550000, 1600000, 1650000, 1700000, 1750000, 
            1800000, 1850000]

def generate_sample_profit_data():
    """サンプルの利益データを生成（データが存在しない場合用）"""
    return [240000, 260000, 280000, 290000, 300000, 
            310000, 320000, 330000, 340000, 350000, 
            360000, 370000] 