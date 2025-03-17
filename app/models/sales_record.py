from app import db
from datetime import datetime

class SalesRecord(db.Model):
    """
    売上記録モデル
    
    各収益事業の月次売上データを管理する。
    ビジネスモデルの種類に応じて、異なる売上計算要素を保持する。
    """
    
    __tablename__ = 'sales_records'

    # 基本情報
    id = db.Column(db.Integer, primary_key=True)
    revenue_business_id = db.Column(db.Integer, db.ForeignKey('revenue_businesses.id'), nullable=False)
    month = db.Column(db.Date, nullable=False)  # 対象月
    
    # 基本売上要素
    unit_price = db.Column(db.Integer)      # 単価
    quantity = db.Column(db.Integer)         # 数量
    total_amount = db.Column(db.Integer, nullable=False)  # 合計金額
    
    # 従量課金モデル用の要素
    usage_amount = db.Column(db.Integer)     # 利用量
    usage_unit_price = db.Column(db.Integer) # 利用単価
    
    # サブスクリプション用の要素
    subscriber_count = db.Column(db.Integer) # 契約者数
    monthly_fee = db.Column(db.Integer)      # 月額料金
    
    # 広告収入用の要素
    ad_impression = db.Column(db.Integer)    # 広告表示回数
    ad_unit_price = db.Column(db.Integer)    # 広告単価
    
    # プロジェクト用の要素
    project_count = db.Column(db.Integer)       # プロジェクト数
    project_unit_price = db.Column(db.Integer)  # プロジェクト単価
    
    # タイムスタンプ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """
        モデルの辞書表現を返す
        
        APIレスポンス用にモデルの情報をシリアライズする
        """
        return {
            'id': self.id,
            'revenue_business_id': self.revenue_business_id,
            'month': self.month.strftime('%Y-%m'),
            'unit_price': self.unit_price,
            'quantity': self.quantity,
            'total_amount': self.total_amount,
            'usage_amount': self.usage_amount,
            'usage_unit_price': self.usage_unit_price,
            'subscriber_count': self.subscriber_count,
            'monthly_fee': self.monthly_fee,
            'ad_impression': self.ad_impression,
            'ad_unit_price': self.ad_unit_price,
            'project_count': self.project_count,
            'project_unit_price': self.project_unit_price
        } 