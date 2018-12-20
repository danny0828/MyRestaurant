"""
 Created by Danny on 2018/12/12
"""
from app.models.base import db
__author__ = 'Danny'


class PayOrderItem(db.Model):
    __tablename__ = 'pay_order_item'

    id = db.Column(db.Integer, primary_key=True)
    pay_order_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue())
    member_id = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    quantity = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    food_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue())
    note = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())









