from flask import Blueprint, render_template, request, jsonify, current_app
from app.models.models import BusinessPlan, PlanItem, CashFlowPlan, CashFlowItem
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import base64
from datetime import datetime
import numpy as np
from sqlalchemy import func
from flask_login import login_required, current_user

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/', methods=['GET'])
@login_required
def analytics_dashboard():
    """分析ダッシュボードを表示"""
    # 過去の事業計画一覧を取得
    business_plans = BusinessPlan.query.filter_by(user_id=current_user.id).all()
    
    return render_template('analytics/dashboard.html', 
                           business_plans=business_plans)

@analytics_bp.route('/plan-comparison', methods=['POST'])
@login_required
def plan_comparison():
    """複数の事業計画を比較分析"""
    plan_ids = request.json.get('plan_ids', [])
    
    if not plan_ids:
        return jsonify({'error': '事業計画が選択されていません'}), 400
    
    # 選択された事業計画を取得
    plans = BusinessPlan.query.filter(
        BusinessPlan.id.in_(plan_ids),
        BusinessPlan.user_id == current_user.id
    ).all()
    
    if not plans:
        return jsonify({'error': '指定された事業計画が見つかりません'}), 404
    
    # 比較データの準備
    comparison_data = []
    for plan in plans:
        # 売上項目の取得
        sales_items = PlanItem.query.filter_by(
            business_plan_id=plan.id,
            category='売上'
        ).all()
        
        # 費用項目の取得
        cost_items = PlanItem.query.filter_by(
            business_plan_id=plan.id,
            category='費用'
        ).all()
        
        # 売上合計
        total_sales = sum([
            sum([
                getattr(item, f'm{i}') or 0 
                for i in range(1, 13)
            ]) 
            for item in sales_items
        ])
        
        # 費用合計
        total_costs = sum([
            sum([
                getattr(item, f'm{i}') or 0 
                for i in range(1, 13)
            ]) 
            for item in cost_items
        ])
        
        # 利益
        profit = total_sales - total_costs
        
        comparison_data.append({
            'plan_id': plan.id,
            'plan_name': plan.name,
            'fiscal_year': plan.fiscal_year,
            'total_sales': total_sales,
            'total_costs': total_costs,
            'profit': profit,
            'profit_margin': (profit / total_sales * 100) if total_sales > 0 else 0
        })
    
    # 可視化用のチャートデータを生成
    chart_data = generate_comparison_charts(comparison_data)
    
    return jsonify({
        'comparison_data': comparison_data,
        'chart_data': chart_data
    })

@analytics_bp.route('/monthly-trend/<int:plan_id>', methods=['GET'])
@login_required
def monthly_trend(plan_id):
    """月次トレンド分析"""
    plan = BusinessPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    
    if not plan:
        return jsonify({'error': '指定された事業計画が見つかりません'}), 404
    
    # 売上項目の取得
    sales_items = PlanItem.query.filter_by(
        business_plan_id=plan_id,
        category='売上'
    ).all()
    
    # 費用項目の取得
    cost_items = PlanItem.query.filter_by(
        business_plan_id=plan_id,
        category='費用'
    ).all()
    
    # 月次データの準備
    monthly_data = []
    
    for month in range(1, 13):
        # 売上合計
        month_sales = sum([getattr(item, f'm{month}') or 0 for item in sales_items])
        
        # 費用合計
        month_costs = sum([getattr(item, f'm{month}') or 0 for item in cost_items])
        
        # 利益
        profit = month_sales - month_costs
        
        monthly_data.append({
            'month': month,
            'sales': month_sales,
            'costs': month_costs,
            'profit': profit,
            'profit_margin': (profit / month_sales * 100) if month_sales > 0 else 0
        })
    
    # チャートデータの生成
    chart_data = generate_monthly_charts(monthly_data, plan.name)
    
    return jsonify({
        'monthly_data': monthly_data,
        'chart_data': chart_data,
        'plan_name': plan.name,
        'fiscal_year': plan.fiscal_year
    })

@analytics_bp.route('/cash-flow-analysis/<int:plan_id>', methods=['GET'])
@login_required
def cash_flow_analysis(plan_id):
    """資金繰り分析"""
    # 事業計画の確認
    plan = BusinessPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    
    if not plan:
        return jsonify({'error': '指定された事業計画が見つかりません'}), 404
    
    # 関連する資金繰り計画を取得
    cash_flow_plan = CashFlowPlan.query.filter_by(business_plan_id=plan_id).first()
    
    if not cash_flow_plan:
        return jsonify({'error': '関連する資金繰り計画が見つかりません'}), 404
    
    # 資金繰り項目を取得
    cash_flow_items = CashFlowItem.query.filter_by(cash_flow_plan_id=cash_flow_plan.id).all()
    
    # 月ごとの入出金データを集計
    monthly_cash_data = []
    
    for month in range(1, 3):  # 最初の2ヶ月のデータを分析
        # 日付ごとの入出金を集計
        dates = ['d5', 'd10', 'd15', 'd20', 'd25', 'end']
        date_data = []
        
        for date in dates:
            column_name = f'm{month}_{date}'
            
            # 収入（売上カテゴリー）
            income_items = [item for item in cash_flow_items if item.category in ['売上', '営業外収入', '財務収入']]
            income = sum([getattr(item, column_name) or 0 for item in income_items])
            
            # 支出（費用カテゴリー）
            expense_items = [item for item in cash_flow_items if item.category in ['費用', '営業外費用', '財務費用']]
            expense = sum([getattr(item, column_name) or 0 for item in expense_items])
            
            # 残高（その時点での収支）
            balance = income - expense
            
            date_data.append({
                'date': f'{month}月{date.replace("d", "")}日' if date != 'end' else f'{month}月末',
                'income': income,
                'expense': expense,
                'balance': balance
            })
        
        monthly_cash_data.append({
            'month': month,
            'date_data': date_data
        })
    
    # チャートデータの生成
    chart_data = generate_cash_flow_charts(monthly_cash_data)
    
    return jsonify({
        'cash_flow_data': monthly_cash_data,
        'chart_data': chart_data,
        'plan_name': plan.name,
        'fiscal_year': plan.fiscal_year
    })

def generate_comparison_charts(comparison_data):
    """事業計画比較のチャートを生成"""
    # Matplotlibでチャートを生成
    plt.figure(figsize=(10, 6))
    
    # データの準備
    plans = [data['plan_name'] for data in comparison_data]
    sales = [data['total_sales'] for data in comparison_data]
    costs = [data['total_costs'] for data in comparison_data]
    profits = [data['profit'] for data in comparison_data]
    
    # 棒グラフ用のX軸位置
    x = np.arange(len(plans))
    width = 0.25  # バーの幅
    
    # 売上、費用、利益の棒グラフ
    plt.bar(x - width, sales, width, label='売上', color='skyblue')
    plt.bar(x, costs, width, label='費用', color='salmon')
    plt.bar(x + width, profits, width, label='利益', color='lightgreen')
    
    plt.xlabel('事業計画')
    plt.ylabel('金額')
    plt.title('事業計画比較')
    plt.xticks(x, plans, rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # 画像をバイト列に変換
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # Base64エンコード
    chart_base64 = base64.b64encode(image_png).decode('utf-8')
    
    # 利益率の円グラフ
    plt.figure(figsize=(8, 8))
    profit_margins = [data['profit_margin'] for data in comparison_data]
    
    plt.pie(profit_margins, labels=plans, autopct='%1.1f%%', 
            shadow=True, startangle=90, colors=['skyblue', 'lightgreen', 'salmon', 'lightgray'])
    plt.axis('equal')
    plt.title('利益率比較')
    
    # 画像をバイト列に変換
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # Base64エンコード
    margin_chart_base64 = base64.b64encode(image_png).decode('utf-8')
    
    plt.close('all')
    
    return {
        'comparison_chart': chart_base64,
        'margin_chart': margin_chart_base64
    }

def generate_monthly_charts(monthly_data, plan_name):
    """月次トレンドのチャートを生成"""
    # Matplotlibでチャートを生成
    plt.figure(figsize=(12, 6))
    
    # データの準備
    months = [data['month'] for data in monthly_data]
    sales = [data['sales'] for data in monthly_data]
    costs = [data['costs'] for data in monthly_data]
    profits = [data['profit'] for data in monthly_data]
    
    # 売上と費用の折れ線グラフ
    plt.plot(months, sales, 'o-', label='売上', color='blue')
    plt.plot(months, costs, 'o-', label='費用', color='red')
    plt.plot(months, profits, 'o-', label='利益', color='green')
    
    plt.xlabel('月')
    plt.ylabel('金額')
    plt.title(f'{plan_name} - 月次推移')
    plt.xticks(months)
    plt.legend()
    plt.grid(True)
    
    # 画像をバイト列に変換
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # Base64エンコード
    trend_chart_base64 = base64.b64encode(image_png).decode('utf-8')
    
    # 積み上げ棒グラフ
    plt.figure(figsize=(12, 6))
    
    plt.bar(months, costs, label='費用', color='salmon')
    plt.bar(months, profits, bottom=costs, label='利益', color='lightgreen')
    
    plt.xlabel('月')
    plt.ylabel('金額')
    plt.title(f'{plan_name} - 構成分析')
    plt.xticks(months)
    plt.legend()
    
    # 画像をバイト列に変換
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # Base64エンコード
    stacked_chart_base64 = base64.b64encode(image_png).decode('utf-8')
    
    plt.close('all')
    
    return {
        'trend_chart': trend_chart_base64,
        'stacked_chart': stacked_chart_base64
    }

def generate_cash_flow_charts(monthly_cash_data):
    """資金繰り分析のチャートを生成"""
    # 時系列データの準備
    all_dates = []
    incomes = []
    expenses = []
    balances = []
    
    for month in monthly_cash_data:
        for date_data in month['date_data']:
            all_dates.append(date_data['date'])
            incomes.append(date_data['income'])
            expenses.append(date_data['expense'])
            balances.append(date_data['balance'])
    
    # 資金繰り推移チャート
    plt.figure(figsize=(14, 6))
    
    plt.plot(all_dates, incomes, 'o-', label='収入', color='blue')
    plt.plot(all_dates, expenses, 'o-', label='支出', color='red')
    plt.plot(all_dates, balances, 'o-', label='残高', color='green')
    
    plt.xlabel('日付')
    plt.ylabel('金額')
    plt.title('資金繰り推移')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # 画像をバイト列に変換
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # Base64エンコード
    cash_flow_chart_base64 = base64.b64encode(image_png).decode('utf-8')
    
    # 累積残高チャート
    plt.figure(figsize=(14, 6))
    
    cumulative_balance = np.cumsum(np.array(incomes) - np.array(expenses))
    
    plt.plot(all_dates, cumulative_balance, 'o-', label='累積残高', color='purple')
    plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
    
    plt.xlabel('日付')
    plt.ylabel('累積残高')
    plt.title('累積資金残高推移')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # 画像をバイト列に変換
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # Base64エンコード
    cumulative_chart_base64 = base64.b64encode(image_png).decode('utf-8')
    
    plt.close('all')
    
    return {
        'cash_flow_chart': cash_flow_chart_base64,
        'cumulative_chart': cumulative_chart_base64
    } 