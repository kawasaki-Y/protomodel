from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app.routes.account_settings import account_settings_bp
from app.models.models import db, AccountItem

# 損益計算書科目設定ページ
@account_settings_bp.route('/pl', methods=['GET'])
@login_required
def pl_accounts():
    return render_template('account_settings/pl_accounts.html', title='損益計算書科目設定')

# 貸借対照表科目設定ページ
@account_settings_bp.route('/bs', methods=['GET'])
@login_required
def bs_accounts():
    return render_template('account_settings/bs_accounts.html', title='貸借対照表科目設定')

# 資金繰り用科目設定ページ
@account_settings_bp.route('/cf', methods=['GET'])
@login_required
def cf_accounts():
    return render_template('account_settings/cf_accounts.html', title='資金繰り用科目設定')

# 資本政策科目設定ページ
@account_settings_bp.route('/capital', methods=['GET'])
@login_required
def capital_accounts():
    return render_template('account_settings/capital_accounts.html', title='資本政策科目設定')

# 損益計算書科目APIエンドポイント

# 科目一覧取得API
@account_settings_bp.route('/api/account-items', methods=['GET'])
@login_required
def get_account_items():
    """科目一覧を取得するAPI"""
    account_items = AccountItem.query.order_by(AccountItem.display_order).all()
    
    result = []
    for item in account_items:
        result.append({
            'id': item.id,
            'code': item.code,
            'name': item.name,
            'category': item.category,
            'sub_category': item.sub_category,
            'display_order': item.display_order
        })
    
    return jsonify(result)

# 科目追加API
@account_settings_bp.route('/api/account-items', methods=['POST'])
@login_required
def add_account_item():
    """科目を追加するAPI"""
    data = request.json
    
    # 必須項目チェック
    if not all(key in data for key in ['name', 'category', 'sub_category']):
        return jsonify({'error': '必須項目が不足しています'}), 400
    
    # 科目コードの自動生成
    category_prefix = '1' if data['category'] == '収益' else '2'
    
    # 同じカテゴリの最大コードを取得
    max_code_item = AccountItem.query.filter(
        AccountItem.code.like(f'{category_prefix}%')
    ).order_by(db.desc(AccountItem.code)).first()
    
    if max_code_item:
        max_code = int(max_code_item.code)
        new_code = str(max_code + 1)
    else:
        new_code = f'{category_prefix}001'  # 初期値
    
    # 新しい科目を作成
    new_item = AccountItem(
        code=new_code,
        name=data['name'],
        category=data['category'],
        sub_category=data['sub_category'],
        display_order=data.get('display_order', 0)
    )
    
    db.session.add(new_item)
    
    try:
        db.session.commit()
        return jsonify({
            'id': new_item.id,
            'code': new_item.code,
            'name': new_item.name,
            'category': new_item.category,
            'sub_category': new_item.sub_category,
            'display_order': new_item.display_order
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 科目編集API
@account_settings_bp.route('/api/account-items/<int:id>', methods=['PUT'])
@login_required
def update_account_item(id):
    """科目を編集するAPI"""
    item = AccountItem.query.get_or_404(id)
    data = request.json
    
    # 変更可能項目の更新
    if 'name' in data:
        item.name = data['name']
    if 'sub_category' in data:
        item.sub_category = data['sub_category']
    if 'display_order' in data:
        item.display_order = data['display_order']
    
    # カテゴリ変更時は科目コードも変更
    if 'category' in data and data['category'] != item.category:
        item.category = data['category']
        category_prefix = '1' if data['category'] == '収益' else '2'
        
        # 同じカテゴリの最大コードを取得
        max_code_item = AccountItem.query.filter(
            AccountItem.code.like(f'{category_prefix}%')
        ).order_by(db.desc(AccountItem.code)).first()
        
        if max_code_item:
            max_code = int(max_code_item.code)
            item.code = str(max_code + 1)
        else:
            item.code = f'{category_prefix}001'  # 初期値
    
    try:
        db.session.commit()
        return jsonify({
            'id': item.id,
            'code': item.code,
            'name': item.name,
            'category': item.category,
            'sub_category': item.sub_category,
            'display_order': item.display_order
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 科目削除API
@account_settings_bp.route('/api/account-items/<int:id>', methods=['DELETE'])
@login_required
def delete_account_item(id):
    """科目を削除するAPI"""
    item = AccountItem.query.get_or_404(id)
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': '科目が削除されました'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 