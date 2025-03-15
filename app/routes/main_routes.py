from flask import Blueprint, render_template, jsonify, redirect, url_for
from app.models.models import db, BusinessPlan, PlanItem, CashFlowPlan, CashFlowItem
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """トップページ/ダッシュボードへリダイレクト"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """ダッシュボード画面"""
    # 事業計画データを取得
    current_plans = BusinessPlan.query.filter_by(plan_type='current').all()
    next_plans = BusinessPlan.query.filter_by(plan_type='next').all()
    cash_flow_plans = CashFlowPlan.query.all()
    
    return render_template('dashboard.html', 
                          current_plans=current_plans,
                          next_plans=next_plans,
                          cash_flow_plans=cash_flow_plans)

@main_bp.route('/api/dashboard/chart-data')
@login_required
def dashboard_chart_data():
    """ダッシュボード用のグラフデータAPIエンドポイント"""
    # 単年事業計画データ
    current_plan = BusinessPlan.query.filter_by(plan_type='current').order_by(BusinessPlan.created_at.desc()).first()
    
    if not current_plan:
        return jsonify({'error': '事業計画データがありません'})
    
    # 売上項目
    sales_items = PlanItem.query.filter_by(business_plan_id=current_plan.id, category='売上').all()
    # 利益項目
    profit_items = PlanItem.query.filter_by(business_plan_id=current_plan.id, category='営業利益').all()
    
    # 資金繰り
    cash_flow = CashFlowPlan.query.filter_by(business_plan_id=current_plan.id).first()
    cash_balance_items = []
    if cash_flow:
        cash_balance_items = CashFlowItem.query.filter_by(
            cash_flow_plan_id=cash_flow.id, 
            category='現金残高'
        ).all()
    
    # 月別データの集計
    months = [f"{i}月" for i in range(current_plan.start_month, 13)] + [f"{i}月" for i in range(1, current_plan.end_month + 1)]
    
    # 売上データ
    sales_data = [0] * len(months)
    for item in sales_items:
        for i, month_num in enumerate(range(current_plan.start_month, current_plan.start_month + len(months))):
            month_num = ((month_num - 1) % 12) + 1  # 1-12の範囲に調整
            month_attr = f"m{month_num}_amount"
            if hasattr(item, month_attr):
                sales_data[i] += getattr(item, month_attr)
    
    # 利益データと資金残高も同様に集計
    profit_data = [0] * len(months)
    cash_data = [0] * len(months)
    
    # レスポンスデータの作成
    chart_data = {
        'labels': months,
        'datasets': [
            {
                'label': '売上',
                'data': sales_data,
                'borderColor': 'rgb(54, 162, 235)',
                'backgroundColor': 'rgba(54, 162, 235, 0.5)',
            },
            {
                'label': '利益',
                'data': profit_data,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.5)',
            },
            {
                'label': '資金残高',
                'data': cash_data,
                'borderColor': 'rgb(255, 159, 64)',
                'backgroundColor': 'rgba(255, 159, 64, 0.5)',
            }
        ]
    }
    
    return jsonify(chart_data) 