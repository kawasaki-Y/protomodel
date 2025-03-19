from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import func

class Business(db.Model):
    """収益事業のマスターデータ"""
    __tablename__ = 'businesses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 事業名
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    products = relationship('Product', back_populates='business', cascade='all, delete-orphan')
    markets = relationship('Market', back_populates='business', cascade='all, delete-orphan')
    revenue_plans = relationship('RevenuePlan', back_populates='business', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Business {self.name}>'

class Product(db.Model):
    """商品・サービスのマスターデータ"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 商品・サービス名
    description = db.Column(db.Text)
    unit_price = db.Column(db.Float)  # 標準単価
    price_unit = db.Column(db.String(30))  # 価格単位（個、時間、月など）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    business = relationship('Business', back_populates='products')
    revenue_details = relationship('RevenueDetail', back_populates='product', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Market(db.Model):
    """顧客・市場のマスターデータ"""
    __tablename__ = 'markets'
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 顧客・市場名
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    business = relationship('Business', back_populates='markets')
    revenue_details = relationship('RevenueDetail', back_populates='market', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Market {self.name}>'

class RevenuePlan(db.Model):
    """売上計画の基本情報"""
    __tablename__ = 'revenue_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)  # 年度
    scenario = db.Column(db.String(30), default='standard')  # シナリオ（標準、楽観、悲観）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    business = relationship('Business', back_populates='revenue_plans')
    details = relationship('RevenueDetail', back_populates='plan', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<RevenuePlan {self.fiscal_year} {self.scenario}>'
    
    @property
    def total_amount(self):
        """計画の年間総売上額を計算"""
        return db.session.query(func.sum(RevenueDetail.amount)).filter(
            RevenueDetail.plan_id == self.id
        ).scalar() or 0

class RevenueDetail(db.Model):
    """売上計画の詳細（月別・商品別・顧客別）"""
    __tablename__ = 'revenue_details'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('revenue_plans.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12の月
    unit_price = db.Column(db.Float)  # 単価
    quantity = db.Column(db.Float)  # 数量
    amount = db.Column(db.Float)  # 金額（unit_price * quantity）
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    plan = relationship('RevenuePlan', back_populates='details')
    product = relationship('Product', back_populates='revenue_details')
    market = relationship('Market', back_populates='revenue_details')
    
    def __repr__(self):
        return f'<RevenueDetail {self.month}月 {self.amount}円>' 