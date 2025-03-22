from app.extensions import db
from datetime import datetime

# 収益計画モデル
class RevenuePlan(db.Model):
    __tablename__ = 'revenue_plans'
    __table_args__ = {'extend_existing': True}  # 既存テーブルの再定義を許可
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('revenue_businesses.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    unit_price = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 月別の数量データはJSONとして保存
    quantities = db.Column(db.JSON, default=dict)

    business = db.relationship('RevenueBusiness', backref='revenue_plans')
    customer = db.relationship('Customer', backref='revenue_plans')
    
    # リレーションシップの修正
    details = db.relationship(
        'RevenuePlanDetail',
        backref='plan',
        lazy=True,
        primaryjoin="and_(RevenuePlan.id==RevenuePlanDetail.plan_id, "
                   "RevenuePlan.business_id==RevenuePlanDetail.business_id)"
    )
    
    def __repr__(self):
        return f'<RevenuePlan {self.id} for business {self.business_id}>'

# 収益計画詳細モデル
class RevenuePlanDetail(db.Model):
    __tablename__ = 'revenue_plan_details'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('revenue_plans.id'), nullable=False)  # 追加
    business_id = db.Column(db.Integer, db.ForeignKey('revenue_businesses.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12の値
    unit_price = db.Column(db.Integer, nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    amount = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップの修正
    business = db.relationship('RevenueBusiness', backref='revenue_plan_details')
    customer = db.relationship('Customer', backref='revenue_plan_details')

    __table_args__ = (
        db.UniqueConstraint('plan_id', 'business_id', 'customer_id', 'month', 
                           name='unique_revenue_plan_detail'),
    )

    def __repr__(self):
        return f'<RevenuePlanDetail {self.id} for plan {self.business_id}>' 