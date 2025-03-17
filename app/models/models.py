from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class BusinessPlan(db.Model):
    """
    事業計画モデル
    """
    __tablename__ = 'business_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(10), nullable=False)  # 年度（例：2023）
    start_month = db.Column(db.String(7), nullable=False)  # 期初月（例：2023-01）
    end_month = db.Column(db.String(7), nullable=False)  # 期末月（例：2023-12）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ - Userへのバックリファレンスを削除
    user = db.relationship('User')
    items = db.relationship('BusinessPlanItem', backref='business_plan', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<BusinessPlan {self.year}>'
    
    @property
    def months(self):
        """
        事業計画の対象月を配列で返す
        """
        from dateutil.parser import parse
        from dateutil.relativedelta import relativedelta
        
        start = parse(self.start_month + "-01")
        end = parse(self.end_month + "-01")
        result = []
        
        current = start
        while current <= end:
            result.append(current.strftime('%Y-%m'))
            current += relativedelta(months=1)
            
        return result

class BusinessPlanItem(db.Model):
    """
    事業計画項目モデル
    """
    __tablename__ = 'business_plan_items'
    
    id = db.Column(db.Integer, primary_key=True)
    business_plan_id = db.Column(db.Integer, db.ForeignKey('business_plans.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('business_plan_items.id'), nullable=True)
    category = db.Column(db.String(50), nullable=False)  # カテゴリ（収益、費用など）
    item_type = db.Column(db.String(20), nullable=False)  # タイプ（親項目、子項目）
    name = db.Column(db.String(100), nullable=False)  # 項目名
    description = db.Column(db.Text, nullable=True)  # 説明
    sort_order = db.Column(db.Integer, default=0)  # 表示順
    
    # 月別金額（各月のカラムを用意）
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
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    parent = db.relationship('BusinessPlanItem', backref=db.backref('children', lazy=True), 
                             remote_side=[id], foreign_keys=[parent_id])
    actual_data = db.relationship('ActualData', back_populates='plan_item', lazy=True)
    
    def __repr__(self):
        return f'<BusinessPlanItem {self.name}>'
    
    @property
    def total_amount(self):
        """
        年間合計金額を返す
        """
        return (self.m1_amount + self.m2_amount + self.m3_amount + self.m4_amount + 
                self.m5_amount + self.m6_amount + self.m7_amount + self.m8_amount + 
                self.m9_amount + self.m10_amount + self.m11_amount + self.m12_amount)
    
    def get_month_amount(self, month_index):
        """
        指定された月のインデックス（1〜12）に対応する金額を返す
        """
        month_amounts = {
            1: self.m1_amount,
            2: self.m2_amount,
            3: self.m3_amount,
            4: self.m4_amount,
            5: self.m5_amount,
            6: self.m6_amount,
            7: self.m7_amount,
            8: self.m8_amount,
            9: self.m9_amount,
            10: self.m10_amount,
            11: self.m11_amount,
            12: self.m12_amount
        }
        return month_amounts.get(month_index, 0)
    
    def set_month_amount(self, month_index, value):
        """
        指定された月のインデックス（1〜12）に対応する金額を設定
        """
        if month_index == 1:
            self.m1_amount = value
        elif month_index == 2:
            self.m2_amount = value
        elif month_index == 3:
            self.m3_amount = value
        elif month_index == 4:
            self.m4_amount = value
        elif month_index == 5:
            self.m5_amount = value
        elif month_index == 6:
            self.m6_amount = value
        elif month_index == 7:
            self.m7_amount = value
        elif month_index == 8:
            self.m8_amount = value
        elif month_index == 9:
            self.m9_amount = value
        elif month_index == 10:
            self.m10_amount = value
        elif month_index == 11:
            self.m11_amount = value
        elif month_index == 12:
            self.m12_amount = value


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
    related_plan_item_id = db.Column(db.Integer, db.ForeignKey('business_plan_items.id'), nullable=True)
    
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
    related_plan_item = relationship('BusinessPlanItem', backref='cash_flow_items')
    
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
    # 権限管理の拡張
    # role = db.Column(db.String(20), default='user')  # 'admin', 'manager', 'user', 'viewer'
    # permissions = db.Column(db.JSON, default=lambda: {
    #     'create_plan': True,
    #     'edit_plan': True,
    #     'delete_plan': False,
    #     'view_all_plans': False,
    #     'manage_users': False
    # })
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
    
    def has_permission(self, permission):
        """特定の権限を持っているか確認する"""
        if self.is_admin:
            return True
        
        # if permission == 'manage_users':
        #     return False
            
        # return self.permissions.get(permission, False)
        
        # 簡略版: 管理者以外は基本的な操作のみ許可
        if permission in ['create_plan', 'edit_plan']:
            return True
        return False
    
    def get_role_display(self):
        """ロール名の表示用文字列を取得する"""
        # roles = {
        #     'admin': '管理者',
        #     'manager': 'マネージャー',
        #     'user': '一般ユーザー',
        #     'viewer': '閲覧専用'
        # }
        # return roles.get(self.role, '不明')
        if self.is_admin:
            return '管理者'
        return '一般ユーザー'
    
    def __repr__(self):
        return f'<User {self.username}>'


class ActualData(db.Model):
    """実績データモデル"""
    __tablename__ = 'actual_data'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_item_id = db.Column(db.Integer, db.ForeignKey('business_plan_items.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12の月
    amount = db.Column(db.Integer, default=0)  # 実績金額
    notes = db.Column(db.Text, nullable=True)  # メモ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    plan_item = relationship('BusinessPlanItem', back_populates='actual_data')
    
    def __repr__(self):
        return f'<ActualData for {self.plan_item.name} Month:{self.month}>'
    
    @property
    def variance(self):
        """計画との差異を計算（実績 - 計画）"""
        plan_amount = self.plan_item.get_amount_for_month(self.month)
        return self.amount - plan_amount
    
    @property
    def variance_percent(self):
        """計画との差異をパーセンテージで計算"""
        plan_amount = self.plan_item.get_amount_for_month(self.month)
        if plan_amount == 0:
            return 0 if self.amount == 0 else float('inf')
        return (self.amount - plan_amount) / abs(plan_amount) * 100 


class AccountItem(db.Model):
    """勘定科目モデル（損益計算書科目など）"""
    __tablename__ = 'account_items'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)  # 科目コード
    name = db.Column(db.String(100), nullable=False)  # 科目名
    category = db.Column(db.String(50), nullable=False)  # 要素: 収益/費用
    sub_category = db.Column(db.String(50), nullable=False)  # 区分: 売上高、売上原価、販管費など
    display_order = db.Column(db.Integer, default=0)  # 表示順
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AccountItem {self.code}: {self.name}>'


class RevenueBusinessModel(db.Model):
    """収益事業モデル"""
    __tablename__ = 'revenue_business_models'
    
    id = db.Column(db.Integer, primary_key=True)
    business_plan_id = db.Column(db.Integer, db.ForeignKey('business_plans.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 事業名
    business_type = db.Column(db.String(50), nullable=False)  # 事業タイプ（単価×数量、サブスクリプション等）
    description = db.Column(db.Text, nullable=True)  # 事業の説明
    
    # 月別売上高
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
    
    # 事業固有のパラメータ（JSON形式で保存）
    parameters = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    business_plan = relationship('BusinessPlan', backref='revenue_models')
    tags = relationship('RevenueTag', secondary='revenue_model_tags', back_populates='revenue_models')
    
    def __repr__(self):
        return f'<RevenueBusinessModel {self.name}>'
    
    @property
    def total_amount(self):
        """年間合計売上高を返す"""
        return sum([
            self.m1_amount, self.m2_amount, self.m3_amount, 
            self.m4_amount, self.m5_amount, self.m6_amount,
            self.m7_amount, self.m8_amount, self.m9_amount,
            self.m10_amount, self.m11_amount, self.m12_amount
        ])
    
    def get_month_amount(self, month_index):
        """指定された月の売上高を返す"""
        month_amounts = {
            1: self.m1_amount, 2: self.m2_amount, 3: self.m3_amount,
            4: self.m4_amount, 5: self.m5_amount, 6: self.m6_amount,
            7: self.m7_amount, 8: self.m8_amount, 9: self.m9_amount,
            10: self.m10_amount, 11: self.m11_amount, 12: self.m12_amount
        }
        return month_amounts.get(month_index, 0)
    
    def calculate_monthly_revenue(self):
        """事業タイプに基づいて月別売上高を計算"""
        if not self.parameters:
            return
            
        if self.business_type == 'unit_sales':
            # 単価×数量の場合
            unit_price = self.parameters.get('unit_price', 0)
            monthly_units = self.parameters.get('monthly_units', {})
            
            for month in range(1, 13):
                units = monthly_units.get(str(month), 0)
                amount = unit_price * units
                self.set_month_amount(month, amount)
                
        elif self.business_type == 'subscription':
            # サブスクリプションの場合
            monthly_fee = self.parameters.get('monthly_fee', 0)
            subscribers = self.parameters.get('subscribers', {})
            
            for month in range(1, 13):
                sub_count = subscribers.get(str(month), 0)
                amount = monthly_fee * sub_count
                self.set_month_amount(month, amount)
    
    def set_month_amount(self, month_index, value):
        """指定された月の売上高を設定"""
        month_map = {
            1: 'm1_amount', 2: 'm2_amount', 3: 'm3_amount',
            4: 'm4_amount', 5: 'm5_amount', 6: 'm6_amount',
            7: 'm7_amount', 8: 'm8_amount', 9: 'm9_amount',
            10: 'm10_amount', 11: 'm11_amount', 12: 'm12_amount'
        }
        if month_index in month_map:
            setattr(self, month_map[month_index], value)

class RevenueTag(db.Model):
    """収益事業のタグモデル"""
    __tablename__ = 'revenue_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    color = db.Column(db.String(7), nullable=False, default='#3490dc')  # タグの表示色
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    revenue_models = relationship('RevenueBusinessModel', secondary='revenue_model_tags', back_populates='tags')
    
    def __repr__(self):
        return f'<RevenueTag {self.name}>'

# 収益事業モデルとタグの中間テーブル
revenue_model_tags = db.Table('revenue_model_tags',
    db.Column('revenue_model_id', db.Integer, db.ForeignKey('revenue_business_models.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('revenue_tags.id'), primary_key=True)
) 