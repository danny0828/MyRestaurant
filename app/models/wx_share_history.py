"""
 Created by Danny on 2018/12/11
"""
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from app.models.base import db
__author__ = 'Danny'


class WxShareHistory(db.Model):
    __tablename__ = 'wx_share_history'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    share_url = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())








