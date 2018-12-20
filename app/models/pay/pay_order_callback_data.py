"""
 Created by Danny on 2018/12/12
"""
from app.models.base import db
__author__ = 'Danny'


class PayOrderCallbackData(db.Model):
    __tablename__ = 'pay_order_callback_data'

    id = db.Column(db.Integer, primary_key=True)
    pay_order_id = db.Column(db.Integer, nullable=False, unique=True, server_default=db.FetchedValue())
    pay_data = db.Column(db.Text, nullable=False)
    refund_data = db.Column(db.Text, nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())









