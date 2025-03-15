from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from app.models.models import db, BusinessPlan, BusinessPlanItem
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