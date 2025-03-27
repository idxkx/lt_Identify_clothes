from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Wardrobe(db.Model):
    """我的衣橱数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    clothing_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.datetime.now)
    
    def to_dict(self):
        """将实例转换为字典"""
        return {
            'id': self.id,
            'image_path': self.image_path,
            'clothing_type': self.clothing_type,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S')
        } 