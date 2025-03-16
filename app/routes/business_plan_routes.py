from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from app.models.models import db, BusinessPlan, BusinessPlanItem, AccountItem
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

business_plan_bp = Blueprint('business_plan', __name__, url_prefix='/business-plan')

@business_plan_bp.route('/current')
@login_required
def current():
    """事業計画表示ページ"""
    return render_template('business_plan/current.html')

@business_plan_bp.route('/items')
@login_required
def items():
    """数値計画入力ページ"""
    return render_template('business_plan/items.html')

@business_plan_bp.route('/next')
@login_required
def next():
    """次年度計画ページ"""
    return render_template('business_plan/next.html')

@business_plan_bp.route('/create', methods=['GET'])
@login_required
def create():
    """事業計画作成画面（GETリクエスト用）"""
    # 現在のページにリダイレクト
    flash('新しい事業計画を作成します。', 'info')
    return redirect(url_for('business_plan.current'))

@business_plan_bp.route('/create', methods=['POST'])
@login_required
def create_plan():
    """新しい事業計画を作成"""
    try:
        # 現在年を取得
        current_year = datetime.now().year
        
        # 新しい事業計画を作成
        new_plan = BusinessPlan(
            year=str(current_year),
            start_month=f"{current_year}-01",  # 1月開始
            end_month=f"{current_year}-12",    # 12月終了
            user_id=current_user.id
        )
        
        db.session.add(new_plan)
        db.session.commit()
        
        # 標準の項目を追加（親項目）
        parent_items = [
            # 収益項目
            {"name": "売上高", "category": "収益", "item_type": "parent", "sort_order": 10},
            {"name": "営業外収益", "category": "収益", "item_type": "parent", "sort_order": 20},
            
            # 費用項目
            {"name": "売上原価", "category": "費用", "item_type": "parent", "sort_order": 100},
            {"name": "販売費及び一般管理費", "category": "費用", "item_type": "parent", "sort_order": 200},
            {"name": "営業外費用", "category": "費用", "item_type": "parent", "sort_order": 300},
        ]
        
        for item_data in parent_items:
            parent_item = BusinessPlanItem(
                business_plan_id=new_plan.id,
                name=item_data["name"],
                category=item_data["category"],
                item_type=item_data["item_type"],
                sort_order=item_data["sort_order"]
            )
            db.session.add(parent_item)
        
        db.session.commit()
        
        # 子項目の追加
        # 親項目を取得
        parent_items = BusinessPlanItem.query.filter_by(business_plan_id=new_plan.id).all()
        parent_dict = {item.name: item for item in parent_items}
        
        # 子項目のデータ
        child_items = [
            # 売上高の子項目
            {"parent": "売上高", "name": "製品売上", "category": "収益", "item_type": "child", "sort_order": 11},
            {"parent": "売上高", "name": "サービス売上", "category": "収益", "item_type": "child", "sort_order": 12},
            
            # 営業外収益の子項目
            {"parent": "営業外収益", "name": "受取利息", "category": "収益", "item_type": "child", "sort_order": 21},
            {"parent": "営業外収益", "name": "受取配当金", "category": "収益", "item_type": "child", "sort_order": 22},
            
            # 売上原価の子項目
            {"parent": "売上原価", "name": "材料費", "category": "費用", "item_type": "child", "sort_order": 101},
            {"parent": "売上原価", "name": "労務費", "category": "費用", "item_type": "child", "sort_order": 102},
            {"parent": "売上原価", "name": "外注費", "category": "費用", "item_type": "child", "sort_order": 103},
            
            # 販管費の子項目
            {"parent": "販売費及び一般管理費", "name": "給与手当", "category": "費用", "item_type": "child", "sort_order": 201},
            {"parent": "販売費及び一般管理費", "name": "法定福利費", "category": "費用", "item_type": "child", "sort_order": 202},
            {"parent": "販売費及び一般管理費", "name": "広告宣伝費", "category": "費用", "item_type": "child", "sort_order": 203},
            {"parent": "販売費及び一般管理費", "name": "旅費交通費", "category": "費用", "item_type": "child", "sort_order": 204},
            {"parent": "販売費及び一般管理費", "name": "通信費", "category": "費用", "item_type": "child", "sort_order": 205},
            {"parent": "販売費及び一般管理費", "name": "消耗品費", "category": "費用", "item_type": "child", "sort_order": 206},
            {"parent": "販売費及び一般管理費", "name": "水道光熱費", "category": "費用", "item_type": "child", "sort_order": 207},
            {"parent": "販売費及び一般管理費", "name": "地代家賃", "category": "費用", "item_type": "child", "sort_order": 208},
            
            # 営業外費用の子項目
            {"parent": "営業外費用", "name": "支払利息", "category": "費用", "item_type": "child", "sort_order": 301},
            {"parent": "営業外費用", "name": "為替差損", "category": "費用", "item_type": "child", "sort_order": 302},
        ]
        
        for item_data in child_items:
            parent_name = item_data["parent"]
            if parent_name in parent_dict:
                child_item = BusinessPlanItem(
                    business_plan_id=new_plan.id,
                    parent_id=parent_dict[parent_name].id,
                    name=item_data["name"],
                    category=item_data["category"],
                    item_type=item_data["item_type"],
                    sort_order=item_data["sort_order"]
                )
                db.session.add(child_item)
        
        db.session.commit()
        
        flash('新しい事業計画を作成しました', 'success')
        return redirect(url_for('business_plan.current'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"事業計画作成エラー: {str(e)}")
        flash('事業計画の作成に失敗しました', 'danger')
        return redirect(url_for('business_plan.current'))

# APIエンドポイント
@business_plan_bp.route('/api/current-plan', methods=['GET'])
@login_required
def api_get_current_plan():
    """現在の事業計画情報を取得するAPI"""
    # ユーザーの最新の事業計画を取得
    plan = BusinessPlan.query.filter_by(user_id=current_user.id).order_by(BusinessPlan.created_at.desc()).first()
    
    # 事業計画がない場合は空のデータを返す
    if not plan:
        return jsonify({
            'exists': False,
            'message': '事業計画がありません'
        })
    
    # 事業計画の基本情報を返す
    return jsonify({
        'exists': True,
        'id': plan.id,
        'year': plan.year,
        'start_month': plan.start_month,
        'end_month': plan.end_month,
        'months': plan.months
    })

@business_plan_bp.route('/api/plan-items', methods=['GET'])
@login_required
def api_get_plan_items():
    """事業計画項目を階層構造で取得するAPI"""
    # 最新の事業計画を取得
    plan = BusinessPlan.query.filter_by(user_id=current_user.id).order_by(BusinessPlan.created_at.desc()).first()
    
    if not plan:
        return jsonify({
            'exists': False,
            'message': '事業計画がありません'
        })
    
    # 親項目を取得
    parent_items = BusinessPlanItem.query.filter_by(
        business_plan_id=plan.id,
        item_type='parent'
    ).order_by(BusinessPlanItem.sort_order).all()
    
    result = []
    
    # 親項目ごとに子項目を含めて結果を構築
    for parent in parent_items:
        # 子項目を取得
        children = BusinessPlanItem.query.filter_by(
            business_plan_id=plan.id,
            parent_id=parent.id
        ).order_by(BusinessPlanItem.sort_order).all()
        
        # 親項目データの構築
        parent_data = {
            'id': parent.id,
            'name': parent.name,
            'category': parent.category,
            'item_type': parent.item_type,
            'sort_order': parent.sort_order,
            'children': [],
            'amounts': {
                'total': parent.total_amount,
                'months': {
                    f'm{i}': parent.get_month_amount(i) for i in range(1, 13)
                }
            }
        }
        
        # 子項目データの追加
        for child in children:
            child_data = {
                'id': child.id,
                'name': child.name,
                'category': child.category,
                'item_type': child.item_type,
                'sort_order': child.sort_order,
                'amounts': {
                    'total': child.total_amount,
                    'months': {
                        f'm{i}': child.get_month_amount(i) for i in range(1, 13)
                    }
                }
            }
            parent_data['children'].append(child_data)
        
        result.append(parent_data)
    
    return jsonify({
        'exists': True,
        'plan_id': plan.id,
        'items': result,
        'months': plan.months
    })

@business_plan_bp.route('/api/plan-items/<int:item_id>', methods=['PUT'])
@login_required
def api_update_plan_item(item_id):
    """事業計画項目を更新するAPI"""
    try:
        data = request.json
        item = BusinessPlanItem.query.get_or_404(item_id)
        
        # 権限チェック - 自分の事業計画の項目のみ更新可能
        plan = BusinessPlan.query.get(item.business_plan_id)
        if plan.user_id != current_user.id:
            return jsonify({'success': False, 'message': '更新権限がありません'}), 403
        
        # 金額のみ更新
        if 'amounts' in data:
            amounts = data['amounts']
            # 月別金額の更新
            for month_key, value in amounts.items():
                if month_key.startswith('m') and month_key[1:].isdigit():
                    month_index = int(month_key[1:])
                    if 1 <= month_index <= 12:
                        item.set_month_amount(month_index, value)
        
        db.session.commit()
        
        # 更新後の項目情報を返す
        return jsonify({
            'success': True,
            'item': {
                'id': item.id,
                'name': item.name,
                'amounts': {
                    'total': item.total_amount,
                    'months': {
                        f'm{i}': item.get_month_amount(i) for i in range(1, 13)
                    }
                }
            }
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"項目更新エラー: {str(e)}")
        return jsonify({'success': False, 'message': f'更新エラー: {str(e)}'}), 400

@business_plan_bp.route('/api/plan-items', methods=['POST'])
@login_required
def api_create_plan_item():
    """新しい事業計画項目を作成するAPI"""
    try:
        data = request.json
        
        # 事業計画IDの取得
        plan_id = data.get('plan_id')
        plan = BusinessPlan.query.get_or_404(plan_id)
        
        # 権限チェック
        if plan.user_id != current_user.id:
            return jsonify({'success': False, 'message': '作成権限がありません'}), 403
        
        # 親項目IDの取得（オプション）
        parent_id = data.get('parent_id')
        
        # 新しい項目の作成
        new_item = BusinessPlanItem(
            business_plan_id=plan_id,
            parent_id=parent_id,
            name=data.get('name', '新規項目'),
            category=data.get('category', '費用'),
            item_type=data.get('item_type', 'child'),
            sort_order=data.get('sort_order', 999)
        )
        
        # 月別金額の設定（存在する場合）
        if 'amounts' in data:
            amounts = data['amounts']
            for month_key, value in amounts.items():
                if month_key.startswith('m') and month_key[1:].isdigit():
                    month_index = int(month_key[1:])
                    if 1 <= month_index <= 12:
                        new_item.set_month_amount(month_index, value)
        
        db.session.add(new_item)
        db.session.commit()
        
        # 作成した項目情報を返す
        return jsonify({
            'success': True,
            'item': {
                'id': new_item.id,
                'name': new_item.name,
                'category': new_item.category,
                'item_type': new_item.item_type,
                'parent_id': new_item.parent_id,
                'sort_order': new_item.sort_order,
                'amounts': {
                    'total': new_item.total_amount,
                    'months': {
                        f'm{i}': new_item.get_month_amount(i) for i in range(1, 13)
                    }
                }
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"項目作成エラー: {str(e)}")
        return jsonify({'success': False, 'message': f'作成エラー: {str(e)}'}), 400

@business_plan_bp.route('/api/plan-items/<int:item_id>', methods=['DELETE'])
@login_required
def api_delete_plan_item(item_id):
    """事業計画項目を削除するAPI"""
    try:
        item = BusinessPlanItem.query.get_or_404(item_id)
        
        # 権限チェック
        plan = BusinessPlan.query.get(item.business_plan_id)
        if plan.user_id != current_user.id:
            return jsonify({'success': False, 'message': '削除権限がありません'}), 403
        
        # 親項目の場合は子項目も削除される（cascade設定済み）
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '項目を削除しました'})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"項目削除エラー: {str(e)}")
        return jsonify({'success': False, 'message': f'削除エラー: {str(e)}'}), 400

@business_plan_bp.route('/pl-planning', methods=['GET'])
@login_required
def pl_planning():
    """損益計算書の数値計画入力画面"""
    # 現在の事業計画を取得
    business_plan = BusinessPlan.query.filter_by(user_id=current_user.id).order_by(BusinessPlan.created_at.desc()).first()
    
    if not business_plan:
        flash('事業計画を先に作成してください', 'warning')
        return redirect(url_for('business_plan.current'))
    
    # 勘定科目データを取得
    account_items = AccountItem.query.order_by(AccountItem.category, AccountItem.sub_category, AccountItem.display_order).all()
    
    # 各区分ごとにグループ化
    account_items_by_category = {}
    for item in account_items:
        if item.sub_category not in account_items_by_category:
            account_items_by_category[item.sub_category] = []
        account_items_by_category[item.sub_category].append(item)
    
    return render_template('business_plan/pl_planning.html', 
                          title='損益計算書 数値計画入力',
                          business_plan=business_plan,
                          account_items_by_category=account_items_by_category)

@business_plan_bp.route('/api/pl-planning', methods=['GET'])
@login_required
def get_pl_planning_data():
    """損益計算書の数値計画データを取得するAPI"""
    # 現在の事業計画を取得
    business_plan = BusinessPlan.query.filter_by(user_id=current_user.id).order_by(BusinessPlan.created_at.desc()).first()
    
    if not business_plan:
        return jsonify({'exists': False})
    
    # 該当する事業計画の項目を取得
    plan_items = BusinessPlanItem.query.filter_by(business_plan_id=business_plan.id).all()
    
    # 結果をJSONで返す
    result = {
        'exists': True,
        'year': business_plan.year,
        'months': business_plan.months,
        'items': []
    }
    
    for item in plan_items:
        item_data = {
            'id': item.id,
            'parent_id': item.parent_id,
            'category': item.category,
            'item_type': item.item_type,
            'name': item.name,
            'description': item.description,
            'sort_order': item.sort_order,
            'months': {}
        }
        
        # 月別データを追加
        for i, month in enumerate(business_plan.months, 1):
            month_index = i % 12 if i % 12 != 0 else 12
            item_data['months'][month] = item.get_month_amount(month_index)
        
        result['items'].append(item_data)
    
    return jsonify(result)

@business_plan_bp.route('/api/pl-planning', methods=['POST'])
@login_required
def save_pl_planning_data():
    """損益計算書の数値計画データを保存するAPI"""
    data = request.json
    
    # 現在の事業計画を取得
    business_plan = BusinessPlan.query.filter_by(user_id=current_user.id).order_by(BusinessPlan.created_at.desc()).first()
    
    if not business_plan:
        return jsonify({'success': False, 'message': '事業計画が見つかりません'}), 404
    
    try:
        # 既存のアイテムを更新/削除し、新規アイテムを追加
        item_data = data.get('items', [])
        
        # 既存の事業計画項目を取得
        existing_items = {item.id: item for item in BusinessPlanItem.query.filter_by(business_plan_id=business_plan.id).all()}
        
        # 送信されたIDリスト
        submitted_ids = [item.get('id') for item in item_data if item.get('id')]
        
        # データベースにあるが送信されていないIDを削除
        for item_id, item in existing_items.items():
            if item_id not in submitted_ids:
                db.session.delete(item)
        
        # 新規アイテムの親子関係マッピング用
        id_mapping = {}
        
        # 各アイテムを処理
        for item in item_data:
            item_id = item.get('id')
            temp_id = item.get('temp_id')  # 新規アイテム識別用の一時ID
            
            # 月別データの取得
            month_data = item.get('months', {})
            
            if item_id and item_id in existing_items:
                # 既存アイテムの更新
                existing_item = existing_items[item_id]
                existing_item.category = item.get('category')
                existing_item.item_type = item.get('item_type')
                existing_item.name = item.get('name')
                existing_item.description = item.get('description', '')
                existing_item.sort_order = item.get('sort_order', 0)
                
                # 親IDの処理（新規アイテムの親の場合）
                parent_id = item.get('parent_id')
                if parent_id in id_mapping:
                    existing_item.parent_id = id_mapping[parent_id]
                else:
                    existing_item.parent_id = parent_id
                
                # 月別データの更新
                for i, month in enumerate(business_plan.months, 1):
                    month_index = i % 12 if i % 12 != 0 else 12
                    month_amount = month_data.get(month, 0)
                    existing_item.set_month_amount(month_index, month_amount)
                
            else:
                # 新規アイテムの追加
                parent_id = item.get('parent_id')
                if parent_id and parent_id in id_mapping:
                    parent_id = id_mapping[parent_id]
                
                new_item = BusinessPlanItem(
                    business_plan_id=business_plan.id,
                    parent_id=parent_id,
                    category=item.get('category'),
                    item_type=item.get('item_type'),
                    name=item.get('name'),
                    description=item.get('description', ''),
                    sort_order=item.get('sort_order', 0)
                )
                
                # 月別データの設定
                for i, month in enumerate(business_plan.months, 1):
                    month_index = i % 12 if i % 12 != 0 else 12
                    month_amount = month_data.get(month, 0)
                    new_item.set_month_amount(month_index, month_amount)
                
                db.session.add(new_item)
                db.session.flush()  # 一時的にコミットして新しいIDを取得
                
                # 親子関係マッピング用に一時IDと実際のIDを記録
                if temp_id:
                    id_mapping[temp_id] = new_item.id
        
        db.session.commit()
        return jsonify({'success': True, 'message': '数値計画を保存しました'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'保存に失敗しました: {str(e)}'}), 500 