"""
 Created by Danny on 2018/12/2
"""
from app.app import app
from flask import render_template, request
from app.libs.log_service import LogService
from app.libs.error import APIException
from werkzeug.exceptions import HTTPException
from app.libs.error_code import ServerError
__author__ = 'Danny'


@app.errorhandler(404)
def error_404(e):
    LogService.add_error_log(str(e))
    if '/v1/' in request.url:
        return APIException('not found', 404)
    return render_template('error/error.html', **{'status': 404, 'msg': '很抱歉！您访问的页面不存在'})


@app.errorhandler(Exception)
def api_error(e):
    if isinstance(e, APIException):
        return e
    if isinstance(e, HTTPException):
        code = e.code
        msg = e.description
        error_code = 1007
        return APIException(msg, code, error_code)
    else:
        LogService.add_error_log(str(e))
        if not app.config['DEBUG']:
            return ServerError()
        else:
            raise e

