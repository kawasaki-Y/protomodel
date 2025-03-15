from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class BusinessPlan(db.Model):
    """事業計画モデル（単年・来期）"""
    __tablename__ = 'business_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    plan_type = db.Column(db.String(20), nullable=False)  # 'current' または 'next'
    fiscal_year = db.Column(db.Integer, nullable=False)
    start_month = db.Column(db.Integer, nullable=False)  # 期初月（1-12）
    end_month = db.Column(db.Integer, nullable=False)    # 期末月（1-12）
    description = db.Column(db.Text, nullable=True)  # 事業計画の概要説明
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 作成者
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    items = relationship('PlanItem', back_populates='business_plan', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<BusinessPlan {self.name}>'


class PlanItem(db.Model):
    """事業計画項目モデル（階層構造）"""
    __tablename__ = 'plan_items'
    
    id = db.Column(db.Integer, primary_key=True)
    business_plan_id = db.Column(db.Integer, db.ForeignKey('business_plans.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('plan_items.id'), nullable=True)
    
    # 項目情報
    category = db.Column(db.String(50), nullable=False)  # 売上/原価/販管費/営業外収支 など
    item_type = db.Column(db.String(20), nullable=False)  # 'header'(見出し) または 'detail'(詳細)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # 金額情報（月別） - 月ごとに別カラム
    m1_amount = db.Column(db.Integer, default=0)
    m2_amount = db.Column(db.Integer, default=0)
    m3_amount = db.Column(db.Integer, default=0)
    m4_amount = db.Column(db.Integer, default=0)
    m5_amount = db.Column(db.Integer, default=0)
    m6_amount = db.Column(db.Integer, default=0)
    m7_amount = db.Column(db.Integer, default=0)
    m8_amount = db.Column(db.Integer, default=0)
    m9_amount = db.Column(db.Integer, default=0)
    m10_amount = db.Column(db.Integer, default=0)
    m11_amount = db.Column(db.Integer, default=0)
    m12_amount = db.Column(db.Integer, default=0)
    
    # 合計値
    total_amount = db.Column(db.Integer, default=0)
    
    # リレーションシップ
    business_plan = relationship('BusinessPlan', back_populates='items')
    children = relationship('PlanItem', 
                           backref=backref('parent', remote_side=[id]),
                           cascade='all, delete-orphan')
    
    def get_amount_for_month(self, month):
        """指定された月の金額を取得する"""
        if 1 <= month <= 12:
            return getattr(self, f'm{month}_amount', 0)
        return 0
    
    def __repr__(self):
        return f'<PlanItem {self.name}>'


class CashFlowPlan(db.Model):
    """資金繰り計画モデル"""
    __tablename__ = 'cash_flow_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    business_plan_id = db.Column(db.Integer, db.ForeignKey('business_plans.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    items = relationship('CashFlowItem', back_populates='cash_flow_plan', cascade='all, delete-orphan')
    business_plan = relationship('BusinessPlan', backref='cash_flow_plans')
    
    def __repr__(self):
        return f'<CashFlowPlan {self.name}>'


class CashFlowItem(db.Model):
    """資金繰り計画項目モデル（階層構造）"""
    __tablename__ = 'cash_flow_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cash_flow_plan_id = db.Column(db.Integer, db.ForeignKey('cash_flow_plans.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('cash_flow_items.id'), nullable=True)
    related_plan_item_id = db.Column(db.Integer, db.ForeignKey('plan_items.id'), nullable=True)
    
    # 項目情報
    category = db.Column(db.String(50), nullable=False)  # 営業収入/営業支出/財務活動 など
    item_type = db.Column(db.String(20), nullable=False)  # 'header'(見出し) または 'detail'(詳細)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # 各月の区切り（5日区切り）ごとの金額
    # 例：1月の場合（m1_d5, m1_d10, m1_d15, m1_d20, m1_d25, m1_end）
    # 各月（12ヶ月）× 6区切り = 72フィールド
    # 1月
    m1_d5 = db.Column(db.Integer, default=0)
    m1_d10 = db.Column(db.Integer, default=0)
    m1_d15 = db.Column(db.Integer, default=0)
    m1_d20 = db.Column(db.Integer, default=0)
    m1_d25 = db.Column(db.Integer, default=0)
    m1_end = db.Column(db.Integer, default=0)
    
    # 2月
    m2_d5 = db.Column(db.Integer, default=0)
    m2_d10 = db.Column(db.Integer, default=0)
    m2_d15 = db.Column(db.Integer, default=0)
    m2_d20 = db.Column(db.Integer, default=0)
    m2_d25 = db.Column(db.Integer, default=0)
    m2_end = db.Column(db.Integer, default=0)
    
    # 3月〜12月も同様のパターンで定義
    # (実際のアプリでは、すべての月のフィールドを定義する必要があります)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    cash_flow_plan = relationship('CashFlowPlan', back_populates='items')
    children = relationship('CashFlowItem', backref=backref('parent', remote_side=[id]), cascade='all, delete-orphan')
    related_plan_item = relationship('PlanItem', backref='cash_flow_items')
    
    def __repr__(self):
        return f'<CashFlowItem {self.name}>'


class User(UserMixin, db.Model):
    """ユーザーモデル"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    business_plans = relationship('BusinessPlan', backref='creator', lazy='dynamic')
    
    def set_password(self, password):
        """パスワードをハッシュ化してセットする"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """パスワードが正しいか確認する"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>' 