"""
 Created by Danny on 2018/11/28
"""
from app.web import user_bp
from flask import render_template, request, jsonify, make_response, redirect
from app.models.user import User
from app.libs.user_service import UserService
import json
from app.libs.url_manager import UrlManager
from flask_login import login_user, logout_user, login_required, current_user
from app.models.base import db
from app.libs.error_code import AjaxSuccess, AjaxFail
__author__ = 'Danny'


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('user/login.html')

    resp = {'code': 200, 'msg': '登录成功', 'data': {}}
    req = request.values
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    # ajax判断
    # if login_name is None or len(login_name) < 1:
    #     resp['code'] = -1
    #     resp['msg'] = "请输入正确的登录用户名"
    #     return jsonify(resp)
    #
    # if login_pwd is None or len(login_pwd) < 1:
    #     resp['code'] = -1
    #     resp['msg'] = "请输入正确的密码"
    #     return jsonify(resp)

    user_info = User.query.filter_by(login_name=login_name).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "请输入正确的登录用户名和密码-1"
        return jsonify(resp)

    if user_info.login_pwd != UserService.gene_pwd(login_pwd, user_info.login_salt):
        resp['code'] = -1
        resp['msg'] = "请输入正确的登录用户名和密码-2"
        return jsonify(resp)

    if user_info.status != 1:
        resp['code'] = -1
        resp['msg'] = "账号已被禁用，请联系管理员处理"
        return jsonify(resp)

    login_user(user_info)
    # response = make_response(json.dumps({'code': 200, 'msg': '登录成功'}))
    # response.set_cookie(app.config['AUTH_COOKIE_NAME'], '%s#%s' % (
    #     UserService.gene_auth_code(user_info), user_info.uid))
    return AjaxSuccess()   # response 使用ajax返回


@user_bp.route("/edit", methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == "GET":
        return render_template("user/edit.html", context={'current': 'edit'})

    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    nickname = req['nickname'] if 'nickname' in req else ''
    email = req['email'] if 'email' in req else ''

    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名"
        return jsonify(resp)

    if email is None or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱"
        return jsonify(resp)

    user_info = current_user
    user_info.nickname = nickname
    user_info.email = email

    with db.auto_commit():
        user_info
    return jsonify(resp)


@user_bp.route("/reset-pwd", methods=['GET', 'POST'])
@login_required
def reset_pwd():
    if request.method == "GET":
        return render_template("user/reset_pwd.html", current='reset-pwd')

    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values

    old_password = req['old_password'] if 'old_password' in req else ''
    new_password = req['new_password'] if 'new_password' in req else ''

    if old_password is None or len(old_password) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的原密码"
        return jsonify(resp)

    if new_password is None or len(new_password) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的新密码"
        return jsonify(resp)

    if old_password == new_password:
        resp['code'] = -1
        resp['msg'] = "请重新输入一个吧，新密码和原密码不能相同哦"
        return jsonify(resp)

    user_info = current_user

    # if user_info.uid == 1:
    #     resp['code'] = -1
    #     resp['msg'] = "该用户是演示账号，不准修改密码和登录用户名"
    #     return jsonify(resp)

    user_info.login_pwd = UserService.gene_pwd(new_password, user_info.login_salt)

    with db.auto_commit():
        user_info

    response = make_response(json.dumps(resp))
    # 修改密码后更新cookie，使可以通过登录拦截器
    # response.set_cookie(app.config['AUTH_COOKIE_NAME'], '%s#%s' % (
    #     UserService.geneAuthCode(user_info), user_info.uid), 60 * 60 * 24 * 120)  # 保存120天
    return response


@user_bp.route("/logout")
@login_required
def logout():
    response = make_response(redirect(UrlManager.build_url("/user/login")))
    logout_user()
    # response.delete_cookie(app.config['AUTH_COOKIE_NAME'])
    return response











