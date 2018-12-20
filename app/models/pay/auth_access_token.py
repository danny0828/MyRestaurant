"""
 Created by Danny on 2018/12/16
"""
from app.models.base import db
__author__ = 'Danny'


class AuthAccessToken(db.Model):
    __tablename__ = 'auth_access_token'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(600), nullable=False, server_default=db.FetchedValue())
    expired_time = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

