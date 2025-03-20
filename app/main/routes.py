from flask import render_template
from flask_login import login_required
from datetime import datetime

@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now()
    
    # 財務データ取得
    sales_plan = 12500000
    sales_actual = 9750000
    profit_plan = 3750000
    profit_actual = 2925000
    cash_balance = 18250000
    cash_previous = 19450000  # 前月比較用
    
    # タスクデータ
    tasks = [
        {
            'title': '月次決算資料の準備',
            'deadline': '2023-04-10',
            'status': '未着手'
        },
        {
            'title': '銀行との融資面談',
            'deadline': '2023-04-15',
            'status': '未着手'
        }
    ]
    
    # 経営戦略データ
    strategies = [
        {
            'title': '新市場参入の検討',
            'date': '2023-04-02',
            'details': '競合分析と市場規模の調査が必要'
        },
        {
            'title': 'コスト削減プラン',
            'date': '2023-04-01',
            'details': '固定費の見直しを行い、20%削減を目指す'
        }
    ]
    
    # 月次売上推移データ（モックデータ）
    sales_chart_data = {
        'labels': ['1月', '2月', '3月', '4月', '5月', '6月'],
        'data': [1300, 1600, 1400, 2100, 1800, 2400]
    }
    
    # 費用内訳データ
    expense_data = {
        '人件費': 35,
        '広告宣伝費': 20,
        '家賃': 30,
        'その他': 15
    }
    
    return render_template('main/dashboard.html',
                          today=today,
                          sales_plan=sales_plan,
                          sales_actual=sales_actual,
                          profit_plan=profit_plan,
                          profit_actual=profit_actual,
                          cash_balance=cash_balance,
                          cash_previous=cash_previous,
                          tasks=tasks,
                          strategies=strategies,
                          sales_chart_data=sales_chart_data,
                          expense_data=expense_data) 