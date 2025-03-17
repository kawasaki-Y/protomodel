from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models.revenue_business import RevenueBusiness
from app.models.sales_record import SalesRecord
from app.extensions import db
from datetime import datetime

revenue_plan_bp = Blueprint('revenue_plan', __name__, url_prefix='/revenue-plan')

@revenue_plan_bp.route('/')
@login_required
def index():
    """
    収益計画のメインページ
    収益モデルごとの一覧を表示
    """
    revenue_businesses = RevenueBusiness.query.filter_by(user_id=current_user.id).all()
    return render_template('revenue_plan/index.html', businesses=revenue_businesses)

@revenue_plan_bp.route('/entry/<int:business_id>')
@login_required
def entry(business_id):
    """
    収益計画の入力ページ
    特定の収益事業モデルの月次売上を入力する
    """
    # 収益モデルの存在確認とアクセス権チェック
    business = RevenueBusiness.query.get_or_404(business_id)
    if business.user_id != current_user.id:
        return redirect(url_for('revenue_plan.index'))
    
    # 既存の売上データを取得
    sales_records = {}
    existing_records = SalesRecord.query.filter_by(revenue_business_id=business_id).all()
    
    for record in existing_records:
        month_key = record.month.strftime('%Y-%m')
        sales_records[month_key] = record
    
    # 今年の月リスト（データがない月も表示するため）
    current_year = datetime.now().year
    months = []
    for month in range(1, 13):
        month_key = f"{current_year}-{month:02d}"
        months.append({
            'key': month_key,
            'name': f"{month}月",
            'record': sales_records.get(month_key)
        })
    
    return render_template(
        'revenue_plan/entry.html', 
        business=business, 
        months=months
    )

@revenue_plan_bp.route('/save/<int:business_id>', methods=['POST'])
@login_required
def save(business_id):
    """
    収益計画データの保存API
    """
    # 収益モデルの存在確認とアクセス権チェック
    business = RevenueBusiness.query.get_or_404(business_id)
    if business.user_id != current_user.id:
        return jsonify({'success': False, 'message': '権限がありません'})
    
    data = request.json
    try:
        month_str = data.get('month')
        month_date = datetime.strptime(month_str, '%Y-%m')
        
        # 既存レコードの検索または新規作成
        record = SalesRecord.query.filter_by(
            revenue_business_id=business_id,
            month=month_date.date()
        ).first()
        
        if not record:
            record = SalesRecord(
                revenue_business_id=business_id,
                month=month_date.date()
            )
        
        # モデルタイプに応じたデータ保存
        model_type = business.model_type
        if model_type == 'unit':
            # 単価×数量モデル
            record.unit_price = data.get('unit_price', 0)
            record.quantity = data.get('quantity', 0)
            record.total_amount = record.unit_price * record.quantity
        elif model_type == 'subscription':
            # サブスクリプションモデル
            record.subscriber_count = data.get('subscriber_count', 0)
            record.monthly_fee = data.get('monthly_fee', 0)
            record.total_amount = record.subscriber_count * record.monthly_fee
        elif model_type == 'advertisement':
            # 広告収入モデル
            record.ad_impression = data.get('ad_impression', 0)
            record.ad_unit_price = data.get('ad_unit_price', 0)
            record.total_amount = record.ad_impression * record.ad_unit_price
        elif model_type == 'project':
            # プロジェクトモデル
            record.project_count = data.get('project_count', 0)
            record.project_unit_price = data.get('project_unit_price', 0)
            record.total_amount = record.project_count * record.project_unit_price
        else:
            # その他のモデル（直接合計額を設定）
            record.total_amount = data.get('total_amount', 0)
        
        if not record.id:
            db.session.add(record)
        
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': '保存しました',
            'record': {
                'id': record.id,
                'total_amount': record.total_amount
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 