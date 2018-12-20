"""
 Created by Danny on 2018/12/2
"""
from app.models.log.app_access_log import AppAccessLog
from app.models.log.app_error_log import AppErrorLog
from flask import request
import json
from app.libs.helper import get_current_date
from app.models.base import db
from flask_login import current_user
__author__ = 'Danny'


class LogService:
    @staticmethod
    def add_access_log():
        target = AppAccessLog()
        target.target_url = request.url
        target.referer_url = request.referrer
        target.ip = request.remote_addr
        target.query_params = json.dumps(request.values.to_dict())
        # if 'current_user' in g and g.current_user is not None:  拦截器方式
        #     target.uid = g.current_user.uid
        if current_user.is_authenticated:
            target.uid = current_user.uid
        target.ua = request.headers.get("User-Agent")
        target.created_time = get_current_date()
        with db.auto_commit():
            db.session.add(target)
        return True

    @staticmethod
    def add_error_log(content):
        if 'favicon.ico' in request.url:
            return
        target = AppErrorLog()
        target.target_url = request.url
        target.referer_url = request.referrer
        target.query_params = json.dumps(request.values.to_dict())
        target.content = content
        target.created_time = get_current_date()
        with db.auto_commit():
            db.session.add(target)
        return True
