from app.models.models import db, AccountItem

def seed_account_items():
    """
    損益計算書勘定科目の初期データを登録します
    """
    # 既存のデータを確認
    existing_items = AccountItem.query.all()
    if existing_items:
        print('既に勘定科目データが登録されています。スキップします。')
        return
    
    # 収益（Revenue）カテゴリの科目
    revenue_items = [
        # 売上高
        {'code': '1001', 'name': '商品売上高', 'category': '収益', 'sub_category': '売上高', 'display_order': 10},
        {'code': '1002', 'name': 'サービス売上高', 'category': '収益', 'sub_category': '売上高', 'display_order': 20},
        
        # 営業外収益
        {'code': '1101', 'name': '受取利息', 'category': '収益', 'sub_category': '営業外収益', 'display_order': 30},
        {'code': '1102', 'name': '受取配当金', 'category': '収益', 'sub_category': '営業外収益', 'display_order': 40},
        {'code': '1103', 'name': '為替差益', 'category': '収益', 'sub_category': '営業外収益', 'display_order': 50},
        {'code': '1104', 'name': '不動産賃貸収入', 'category': '収益', 'sub_category': '営業外収益', 'display_order': 60},
        
        # 特別利益
        {'code': '1201', 'name': '固定資産売却益', 'category': '収益', 'sub_category': '特別利益', 'display_order': 70},
        {'code': '1202', 'name': '保険金収入', 'category': '収益', 'sub_category': '特別利益', 'display_order': 80},
        {'code': '1203', 'name': '訴訟による賠償金', 'category': '収益', 'sub_category': '特別利益', 'display_order': 90},
    ]
    
    # 費用（Expenses）カテゴリの科目
    expense_items = [
        # 売上原価
        {'code': '2001', 'name': '材料費', 'category': '費用', 'sub_category': '売上原価', 'display_order': 100},
        {'code': '2002', 'name': '労務費', 'category': '費用', 'sub_category': '売上原価', 'display_order': 110},
        {'code': '2003', 'name': '外注費', 'category': '費用', 'sub_category': '売上原価', 'display_order': 120},
        {'code': '2004', 'name': '製造間接費', 'category': '費用', 'sub_category': '売上原価', 'display_order': 130},
        
        # 販売費及び一般管理費（販管費）
        {'code': '2101', 'name': '広告宣伝費', 'category': '費用', 'sub_category': '販売費及び一般管理費', 'display_order': 140},
        {'code': '2102', 'name': '給与・賞与', 'category': '費用', 'sub_category': '販売費及び一般管理費', 'display_order': 150},
        {'code': '2103', 'name': '旅費交通費', 'category': '費用', 'sub_category': '販売費及び一般管理費', 'display_order': 160},
        {'code': '2104', 'name': '通信費', 'category': '費用', 'sub_category': '販売費及び一般管理費', 'display_order': 170},
        {'code': '2105', 'name': '減価償却費', 'category': '費用', 'sub_category': '販売費及び一般管理費', 'display_order': 180},
        {'code': '2106', 'name': '賃貸料', 'category': '費用', 'sub_category': '販売費及び一般管理費', 'display_order': 190},
        {'code': '2107', 'name': '水道光熱費', 'category': '費用', 'sub_category': '販売費及び一般管理費', 'display_order': 200},
        
        # 営業外費用
        {'code': '2201', 'name': '支払利息', 'category': '費用', 'sub_category': '営業外費用', 'display_order': 210},
        {'code': '2202', 'name': '為替差損', 'category': '費用', 'sub_category': '営業外費用', 'display_order': 220},
        {'code': '2203', 'name': '投資損失', 'category': '費用', 'sub_category': '営業外費用', 'display_order': 230},
        {'code': '2204', 'name': '不動産賃貸費用', 'category': '費用', 'sub_category': '営業外費用', 'display_order': 240},
        
        # 特別損失
        {'code': '2301', 'name': '固定資産売却損', 'category': '費用', 'sub_category': '特別損失', 'display_order': 250},
        {'code': '2302', 'name': '災害による損失', 'category': '費用', 'sub_category': '特別損失', 'display_order': 260},
        {'code': '2303', 'name': '訴訟による賠償金', 'category': '費用', 'sub_category': '特別損失', 'display_order': 270},
    ]
    
    # 全データをマージ
    all_items = revenue_items + expense_items
    
    # データベースに登録
    for item_data in all_items:
        item = AccountItem(
            code=item_data['code'],
            name=item_data['name'],
            category=item_data['category'],
            sub_category=item_data['sub_category'],
            display_order=item_data['display_order']
        )
        db.session.add(item)
    
    # コミット
    try:
        db.session.commit()
        print('勘定科目の初期データを登録しました。登録数: {}'.format(len(all_items)))
    except Exception as e:
        db.session.rollback()
        print('勘定科目の初期データ登録に失敗しました: {}'.format(str(e)))

if __name__ == '__main__':
    # このスクリプトを直接実行する場合
    from flask import Flask
    from app import create_app
    
    app = create_app()
    with app.app_context():
        seed_account_items() 