"""
 Created by Danny on 2018/12/18
"""
from app.models.base import db

__author__ = 'Danny'


class StatDailySite(db.Model):
    __tablename__ = 'stat_daily_site'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    total_pay_money = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    total_member_count = db.Column(db.Integer, nullable=False)
    total_new_member_count = db.Column(db.Integer, nullable=False)
    total_order_count = db.Column(db.Integer, nullable=False)
    total_shared_count = db.Column(db.Integer, nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
