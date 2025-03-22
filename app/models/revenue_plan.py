from app.extensions import db
from datetime import datetime

# 収益計画モデル
class RevenuePlan(db.Model):
    __tablename__ = 'revenue_plans'
    __table_args__ = {'extend_existing': True}  # 既存テーブルの再定義を許可
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('revenue_businesses.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # リレーションシップを完全修飾パスで定義
    details = db.relationship('app.models.revenue_plan.RevenuePlanDetail', backref='plan', lazy=True)
    
    def __repr__(self):
        return f'<RevenuePlan {self.id} for business {self.business_id}>'

# 収益計画詳細モデル
class RevenuePlanDetail(db.Model):
    __tablename__ = 'revenue_plan_details'
    __table_args__ = {'extend_existing': True}  # 既存テーブルの再定義を許可
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('revenue_plans.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, default=0)  # quantity * unit_price
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<RevenuePlanDetail {self.id} for plan {self.plan_id}>' 