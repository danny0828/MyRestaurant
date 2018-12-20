"""
 Created by Danny on 2018/12/3
"""
from app.libs.error import APIException
__author__ = 'Danny'


class Success(APIException):
    code = 200
    msg = '操作成功'
    error_code = 0


class ServerError(APIException):
    code = 500
    msg = 'sorry, we made a mistake (*￣︶￣)!'
    error_code = 999


class ParameterException(APIException):
    code = 400
    msg = 'param is invalid'
    error_code = 2005


class AuthFailed(APIException):
    code = 401  # 授权失败（账号、密码不匹配）
    error_code = 2006
    msg = 'authorization failed'


class Forbidden(APIException):
    code = 403  # 禁止访问（权限不够）
    error_code = 1004
    msg = 'forbidden, is not scope'


class NotFound(APIException):
    code = 404
    msg = 'the resource are not found O__O...'
    error_code = 1001


class AjaxSuccess(APIException):
    code = 200
    msg = '操作成功'
    error_code = 0


class AjaxFail(APIException):
    code = -1
    msg = '操作失败'
    error_code = -1










