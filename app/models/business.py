from app.extensions import db
from datetime import datetime

# 収益事業モデル
class RevenueBusiness(db.Model):
    __tablename__ = 'revenue_businesses'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # リレーションシップの定義を修正
    plan_refs = db.relationship('RevenuePlan', back_populates='business')
    services = db.relationship('Service', backref='business', lazy=True)
    # customersのbackref名を変更
    customers = db.relationship('Customer', back_populates='revenue_business', lazy=True)
    
    def __repr__(self):
        return f'<RevenueBusiness {self.name}>'

# サービスモデル
class Service(db.Model):
    __tablename__ = 'services'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    business_id = db.Column(db.Integer, db.ForeignKey('revenue_businesses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Service {self.name}>'

# 顧客モデル
class Customer(db.Model):
    __tablename__ = 'customers'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('revenue_businesses.id'), nullable=False)
    price_factor = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップの定義を修正
    revenue_business = db.relationship('RevenueBusiness', back_populates='customers')
    # backrefを使用せず、back_populatesを使用して双方向関係を定義
    revenue_plans = db.relationship('RevenuePlan', back_populates='customer_ref', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.name}>' 