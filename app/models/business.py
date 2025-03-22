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
    
    services = db.relationship('Service', backref='business', lazy=True)
    customers = db.relationship('Customer', backref='business', lazy=True)
    
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
    price_factor = db.Column(db.Float, default=1.0)  # 価格調整係数
    business_id = db.Column(db.Integer, db.ForeignKey('revenue_businesses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class RevenuePlanValue(db.Model):
    __tablename__ = 'revenue_plan_values'
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('revenue_businesses.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 0-11の値で月を表す
    value = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('business_id', 'customer_id', 'service_id', 'month', name='unique_revenue_plan_value'),
    ) 