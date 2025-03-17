from app.extensions import db
from datetime import datetime
import json

class RevenueBusiness(db.Model):
    """
    収益事業モデル
    
    ビジネスモデルの種類や売上予測のための基本情報を管理する。
    各ユーザーが作成した収益事業の情報を保持する。
    """
    
    __tablename__ = 'revenue_businesses'

    # 基本情報
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # 作成者のID
    name = db.Column(db.String(255), nullable=False)      # 事業名
    model_type = db.Column(db.String(50), nullable=False) # ビジネスモデルの種類
    description = db.Column(db.Text)                      # 事業の説明
    _tags = db.Column('tags', db.Text)                   # タグ（JSON形式で保存）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    sales_records = db.relationship('SalesRecord', backref='revenue_business', lazy=True)

    # タグのプロパティ（JSON形式での保存・取得を隠蔽）
    @property
    def tags(self):
        """タグリストの取得"""
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value):
        """タグリストの保存"""
        self._tags = json.dumps(value) if value else '[]'

    def to_dict(self):
        """
        モデルの辞書表現を返す
        
        APIレスポンス用にモデルの情報をシリアライズする
        """
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'description': self.description,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 