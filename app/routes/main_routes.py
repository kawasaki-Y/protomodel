from flask import Blueprint, render_template, jsonify, redirect, url_for
from app.models.models import db, BusinessPlan, BusinessPlanItem, CashFlowPlan, CashFlowItem
from flask_login import login_required, current_user
from app.models.revenue_business import RevenueBusiness
from app.models.sales_record import SalesRecord
from datetime import datetime, timedelta
import random

# Blueprintの定義
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """
    アプリケーションのトップページ
    未ログインならログインページへ、ログイン済みならダッシュボードへリダイレクト
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/home')
def home():
    """ホーム画面（未ログイン時のランディングページ）"""
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    ダッシュボード画面
    経営情報の概要、各種グラフ、タスク、メモなどを表示
    """
    # 現在の日時を取得
    current_datetime = datetime.now()
    
    # 元気が出るようなランダムメッセージ
    motivational_messages = [
        "今日も最高の一日にしましょう！",
        "小さな一歩が大きな変化を生みます",
        "計画があれば、未来は明るい",
        "データに基づく意思決定が成功への鍵です",
        "今日の努力が明日の成果につながります",
        "課題を見つけるのは簡単、解決策を見つけるのが経営者の仕事です",
        "常に顧客視点で考えましょう",
        "正しい質問が正しい答えを導きます"
    ]
    
    # ランダムなメッセージを選択
    random_message = random.choice(motivational_messages)
    
    # ダミーデータ - 実際はDBからデータを取得
    progress_data = {
        'sales': {'plan': 1000000, 'actual': 850000, 'progress_rate': 85},
        'profit': {'plan': 300000, 'actual': 280000, 'progress_rate': 93},
        'cash': {'balance': 5200000, 'previous_month': 4800000, 'change_rate': 8.3}
    }
    
    # クイックリンクの定義
    quick_links = [
        {
            'name': '収益計画',
            'description': '売上計画の作成と管理',
            'url': url_for('revenue_plan.index'),
            'icon': 'chart-line'
        },
        {
            'name': '事業計画',
            'description': '年度事業計画の確認',
            'url': url_for('main.dashboard'),  # 適切なURLに変更してください
            'icon': 'file-alt'
        },
        {
            'name': '実績入力',
            'description': '月次実績の入力',
            'url': '#',  # 適切なURLに変更してください
            'icon': 'keyboard'
        }
    ]
    
    # タスクリスト
    tasks = [
        {'id': 1, 'title': '月次決算資料の準備', 'deadline': '2023-04-10', 'status': 'pending'},
        {'id': 2, 'title': '銀行との融資面談', 'deadline': '2023-04-15', 'status': 'pending'},
        {'id': 3, 'title': '新規事業計画の見直し', 'deadline': '2023-04-20', 'status': 'in_progress'}
    ]
    
    # 戦略メモ
    strategy_notes = [
        {'id': 1, 'title': '新市場参入の検討', 'content': '競合分析と市場規模の調査が必要', 'created_at': '2023-04-02'},
        {'id': 2, 'title': 'コスト削減プラン', 'content': '固定費の見直しを行い、20%削減を目指す', 'created_at': '2023-04-01'}
    ]
    
    return render_template(
        'dashboard.html',
        current_datetime=current_datetime,
        random_message=random_message,
        progress_data=progress_data,
        quick_links=quick_links,
        tasks=tasks,
        strategy_notes=strategy_notes
    )

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