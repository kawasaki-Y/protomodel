from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.models import db, BusinessPlan, BusinessPlanItem, ActualData
from app.routes.auth_routes import permission_required
from sqlalchemy import and_
import json
from datetime import datetime
import calendar

actual_data_bp = Blueprint('actual_data', __name__, url_prefix='/actual-data')

@actual_data_bp.route('/')
@login_required
def index():
    """実績データ入力ページのメイン画面"""
    # 利用可能な事業計画一覧を取得
    if current_user.has_permission('view_all_plans'):
        # 全ての計画を表示できる権限がある場合
        plans = BusinessPlan.query.order_by(BusinessPlan.fiscal_year.desc()).all()
    else:
        # 自分が作成した計画のみ
        plans = BusinessPlan.query.filter_by(user_id=current_user.id).order_by(BusinessPlan.fiscal_year.desc()).all()
    
    return render_template('actual_data/index.html', plans=plans)

@actual_data_bp.route('/plan/<int:plan_id>')
@login_required
def plan_actual(plan_id):
    """特定の事業計画の実績入力画面"""
    plan = BusinessPlan.query.get_or_404(plan_id)
    
    # 権限チェック
    if not current_user.has_permission('view_all_plans') and plan.user_id != current_user.id:
        flash('このプランにアクセスする権限がありません', 'danger')
        return redirect(url_for('actual_data.index'))
    
    # 計画の全項目を階層構造で取得
    root_items = BusinessPlanItem.query.filter_by(
        business_plan_id=plan_id,
        parent_id=None
    ).order_by(BusinessPlanItem.sort_order).all()
    
    return render_template('actual_data/plan_actual.html', plan=plan, root_items=root_items)

@actual_data_bp.route('/plan/<int:plan_id>/month/<int:month>')
@login_required
def month_actual(plan_id, month):
    """特定の事業計画の特定月の実績入力画面"""
    # 1-12の月チェック
    if month < 1 or month > 12:
        flash('無効な月が指定されました', 'danger')
        return redirect(url_for('actual_data.plan_actual', plan_id=plan_id))
    
    plan = BusinessPlan.query.get_or_404(plan_id)
    
    # 権限チェック
    if not current_user.has_permission('view_all_plans') and plan.user_id != current_user.id:
        flash('このプランにアクセスする権限がありません', 'danger')
        return redirect(url_for('actual_data.index'))
    
    # 計画の詳細項目を取得（ヘッダー項目を除く）
    detail_items = BusinessPlanItem.query.filter_by(
        business_plan_id=plan_id, 
        item_type='detail'
    ).order_by(BusinessPlanItem.category, BusinessPlanItem.sort_order).all()
    
    # 各項目の実績データを取得
    for item in detail_items:
        actual = ActualData.query.filter_by(plan_item_id=item.id, month=month).first()
        if actual:
            item.actual_amount = actual.amount
            item.actual_notes = actual.notes
        else:
            item.actual_amount = 0
            item.actual_notes = ""
    
    # 月の日本語表記を取得
    month_names = ["", "1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    month_name = month_names[month]
    
    return render_template(
        'actual_data/month_actual.html', 
        plan=plan, 
        items=detail_items, 
        month=month,
        month_name=month_name
    )

@actual_data_bp.route('/plan/<int:plan_id>/month/<int:month>/save', methods=['POST'])
@login_required
@permission_required('edit_plan')
def save_month_actual(plan_id, month):
    """特定の事業計画の特定月の実績を保存"""
    # 1-12の月チェック
    if month < 1 or month > 12:
        return jsonify({'status': 'error', 'message': '無効な月が指定されました'}), 400
    
    plan = BusinessPlan.query.get_or_404(plan_id)
    
    # 権限チェック
    if not current_user.has_permission('view_all_plans') and plan.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'このプランにアクセスする権限がありません'}), 403
    
    try:
        # フォームデータを取得
        data = request.get_json()
        
        for item_data in data:
            item_id = int(item_data.get('item_id'))
            amount = int(item_data.get('amount', 0))
            notes = item_data.get('notes', '')
            
            # 該当項目が存在するか確認
            item = BusinessPlanItem.query.get(item_id)
            if not item or item.business_plan_id != plan_id:
                continue
            
            # 既存の実績データを検索、なければ新規作成
            actual = ActualData.query.filter_by(plan_item_id=item_id, month=month).first()
            
            if not actual:
                actual = ActualData(
                    plan_item_id=item_id,
                    month=month,
                    amount=amount,
                    notes=notes
                )
                db.session.add(actual)
            else:
                actual.amount = amount
                actual.notes = notes
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '実績データが保存されました'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'エラーが発生しました: {str(e)}'}), 500

@actual_data_bp.route('/plan/<int:plan_id>/comparison')
@login_required
def plan_comparison(plan_id):
    """計画と実績の比較画面"""
    plan = BusinessPlan.query.get_or_404(plan_id)
    
    # 権限チェック
    if not current_user.has_permission('view_all_plans') and plan.user_id != current_user.id:
        flash('このプランにアクセスする権限がありません', 'danger')
        return redirect(url_for('actual_data.index'))
    
    # 主要カテゴリの項目を取得（売上・利益など）
    main_categories = ['売上', '原価', '売上総利益', '販管費', '営業利益']
    summary_items = {}
    
    for category in main_categories:
        items = BusinessPlanItem.query.filter_by(
            business_plan_id=plan_id,
            category=category,
            item_type='detail'
        ).all()
        
        if items:
            summary_items[category] = items
    
    # 月ごとの集計データを準備
    months_data = []
    
    for month in range(1, 13):
        # 1ヶ月分のデータ
        month_data = {
            'month': month,
            'categories': {}
        }
        
        for category, items in summary_items.items():
            # カテゴリごとの集計
            category_data = {
                'plan_total': 0,
                'actual_total': 0,
                'variance': 0,
                'variance_percent': 0,
                'items': []
            }
            
            for item in items:
                # 計画値
                plan_amount = item.get_amount_for_month(month)
                
                # 実績値
                actual = ActualData.query.filter_by(plan_item_id=item.id, month=month).first()
                actual_amount = actual.amount if actual else 0
                
                # 差異計算
                variance = actual_amount - plan_amount
                variance_percent = 0
                if plan_amount != 0:
                    variance_percent = (variance / abs(plan_amount)) * 100
                
                # 項目データ
                item_data = {
                    'id': item.id,
                    'name': item.name,
                    'plan': plan_amount,
                    'actual': actual_amount,
                    'variance': variance,
                    'variance_percent': variance_percent
                }
                
                category_data['items'].append(item_data)
                category_data['plan_total'] += plan_amount
                category_data['actual_total'] += actual_amount
            
            # カテゴリ全体の差異
            category_data['variance'] = category_data['actual_total'] - category_data['plan_total']
            if category_data['plan_total'] != 0:
                category_data['variance_percent'] = (category_data['variance'] / abs(category_data['plan_total'])) * 100
            
            month_data['categories'][category] = category_data
        
        months_data.append(month_data)
    
    # 月の名前リスト
    month_names = ["", "1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    
    return render_template(
        'actual_data/comparison.html',
        plan=plan,
        months_data=months_data,
        month_names=month_names,
        categories=main_categories
    )

@actual_data_bp.route('/api/chart-data/<int:plan_id>')
@login_required
def api_chart_data(plan_id):
    """チャート用のデータAPIエンドポイント"""
    plan = BusinessPlan.query.get_or_404(plan_id)
    
    # 権限チェック
    if not current_user.has_permission('view_all_plans') and plan.user_id != current_user.id:
        return jsonify({'error': 'アクセス権限がありません'}), 403
    
    # 売上と利益のデータを取得
    sales_items = BusinessPlanItem.query.filter_by(business_plan_id=plan_id, category='売上').all()
    profit_items = BusinessPlanItem.query.filter_by(business_plan_id=plan_id, category='営業利益').all()
    
    # 月ごとのデータを準備
    months = list(range(1, 13))
    sales_plan_data = [0] * 12
    sales_actual_data = [0] * 12
    profit_plan_data = [0] * 12
    profit_actual_data = [0] * 12
    
    # 売上データ集計
    for item in sales_items:
        for month in months:
            # 計画値
            sales_plan_data[month-1] += item.get_amount_for_month(month)
            
            # 実績値
            actual = ActualData.query.filter_by(plan_item_id=item.id, month=month).first()
            if actual:
                sales_actual_data[month-1] += actual.amount
    
    # 利益データ集計
    for item in profit_items:
        for month in months:
            # 計画値
            profit_plan_data[month-1] += item.get_amount_for_month(month)
            
            # 実績値
            actual = ActualData.query.filter_by(plan_item_id=item.id, month=month).first()
            if actual:
                profit_actual_data[month-1] += actual.amount
    
    # 累計データの計算
    sales_plan_cumulative = []
    sales_actual_cumulative = []
    profit_plan_cumulative = []
    profit_actual_cumulative = []
    
    total_sales_plan = 0
    total_sales_actual = 0
    total_profit_plan = 0
    total_profit_actual = 0
    
    for i in range(12):
        total_sales_plan += sales_plan_data[i]
        total_sales_actual += sales_actual_data[i]
        total_profit_plan += profit_plan_data[i]
        total_profit_actual += profit_actual_data[i]
        
        sales_plan_cumulative.append(total_sales_plan)
        sales_actual_cumulative.append(total_sales_actual)
        profit_plan_cumulative.append(total_profit_plan)
        profit_actual_cumulative.append(total_profit_actual)
    
    # レスポンスデータ
    response_data = {
        'labels': ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        'monthly': {
            'sales': {
                'plan': sales_plan_data,
                'actual': sales_actual_data
            },
            'profit': {
                'plan': profit_plan_data,
                'actual': profit_actual_data
            }
        },
        'cumulative': {
            'sales': {
                'plan': sales_plan_cumulative,
                'actual': sales_actual_cumulative
            },
            'profit': {
                'plan': profit_plan_cumulative,
                'actual': profit_actual_cumulative
            }
        }
    }
    
    return jsonify(response_data) 