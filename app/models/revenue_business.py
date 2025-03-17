from app import db
from datetime import datetime
import json

class RevenueBusiness(db.Model):
    __tablename__ = 'revenue_businesses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    _tags = db.Column('tags', db.Text)  # JSON形式で保存
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    sales_records = db.relationship('SalesRecord', backref='revenue_business', lazy=True)

    @property
    def tags(self):
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value):
        self._tags = json.dumps(value) if value else '[]'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'description': self.description,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 