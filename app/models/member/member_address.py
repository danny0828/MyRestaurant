"""
 Created by Danny on 2018/12/17
"""
from app.models.base import Base, db
__author__ = 'Danny'


class MemberAddress(Base):
    __tablename__ = 'member_address'
    __table_args__ = (
        db.Index('idx_member_id_status', 'member_id', 'status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    nickname = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    mobile = db.Column(db.String(11), nullable=False, server_default=db.FetchedValue())
    province_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    province_str = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    city_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    city_str = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    area_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    area_str = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    address = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    is_default = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    def keys(self):
        return ['nickname', 'mobile', 'province_id', 'province_str',
                'city_id', 'city_str', 'area_id', 'area_str', 'address', 'is_default']









