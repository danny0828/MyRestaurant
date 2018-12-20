"""
 Created by Danny on 2018/12/18
"""
from app.models.base import db
__author__ = 'Danny'


class StatDailyFood(db.Model):
    __tablename__ = 'stat_daily_food'
    __table_args__ = (
        db.Index('date_food_id', 'date', 'food_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    food_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    total_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    total_pay_money = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

