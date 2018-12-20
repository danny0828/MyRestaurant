"""
 Created by Danny on 2018/11/28
"""
from app.web import account_bp
from flask import render_template, request, current_app, redirect, jsonify
from app.models.user import User
from flask_login import login_required, current_user, logout_user
from app.libs.helper import i_pagination, get_current_date
from app.libs.url_manager import UrlManager
from app.libs.user_service import UserService
from app.models.base import db
from sqlalchemy import or_
from app.models.log.app_access_log import AppAccessLog
from app.libs.error_code import AjaxSuccess, AjaxFail
__author__ = 'Danny'


@account_bp.route("/index")
@login_required
def index():
    # LogService.add_access_log()
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = User.query

    if 'mix_kw' in req:
        rule = or_(User.nickname.ilike("%{0}%".format(req['mix_kw'])),
                   User.mobile.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter(rule)

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(User.status == int(req['status']))

    page_params = {
        'total': query.count(),
        'page_size': current_app.config['PAGE_SIZE'],
        'page': page,
        'display': current_app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }
    pages = i_pagination(page_params)
    offset = (page - 1) * current_app.config['PAGE_SIZE']
    limit = current_app.config['PAGE_SIZE'] * page

    list = query.order_by(User.uid.desc()).all()[offset:limit]
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['status_mapping'] = current_app.config['STATUS_MAPPING']
    return render_template("account/index.html", **resp_data)


@account_bp.route("/info")
@login_required
def info():
    resp_data = {}
    req = request.args           # 参数少用args
    # reqv = request.values      # 参数多用values
    uid = int(req.get('id', 0))
    reback_url = UrlManager.build_url("/account/index")
    if uid < 1:
        return redirect(reback_url)

    info = User.query.filter_by(uid=uid).first()
    if not info:
        return redirect(reback_url)

    access_list = AppAccessLog.query.filter_by(uid=uid).order_by(AppAccessLog.id.desc()).limit(10).all()
    resp_data['info'] = info
    resp_data['access_list'] = access_list
    return render_template("account/info.html", **resp_data)


@account_bp.route("/set", methods=["GET", "POST"])
@login_required
def set():
    default_pwd = "******"
    if request.method == "GET":
        resp_data = {}
        req = request.args
        uid = int(req.get("id", 0))
        info = None
        if uid:
            info = User.query.filter_by(uid=uid).first()
        resp_data['info'] = info
        return render_template("account/set.html", **resp_data)

    req = request.values

    id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    mobile = req['mobile'] if 'mobile' in req else ''
    email = req['email'] if 'email' in req else ''
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    if nickname is None or len(nickname) < 1:
        return AjaxFail('请输入符合规范的姓名')

    if mobile is None or len(mobile) < 1:
        return AjaxFail('请输入符合规范的手机号码')

    if email is None or len(email) < 1:
        return AjaxFail('请输入符合规范的邮箱')

    if login_name is None or len(login_name) < 1:
        return AjaxFail('请输入符合规范的登录用户名')

    if login_pwd is None or len(email) < 6:
        return AjaxFail('请输入符合规范的登录密码')

    has_in = User.query.filter(User.login_name == login_name, User.uid != id).first()
    if has_in:
        return AjaxFail('该登录名已存在，请换一个试试')

    user_info = User.query.filter_by(uid=id).first()
    if user_info:
        model_user = user_info
    else:
        model_user = User()
        model_user.created_time = get_current_date()
        model_user.login_salt = UserService.gene_salt()

    model_user.nickname = nickname
    model_user.mobile = mobile
    model_user.email = email
    model_user.login_name = login_name
    if login_pwd != default_pwd:
        # if user_info and user_info.uid == 1:
        #     resp['code'] = -1
        #     resp['msg'] = "该用户是演示账号，不准修改密码和登录用户名"
        #     return jsonify(resp)
        model_user.login_pwd = UserService.gene_pwd(login_pwd, model_user.login_salt)

    model_user.updated_time = get_current_date()
    with db.auto_commit():
        db.session.add(model_user)
    return AjaxSuccess()


@account_bp.route("/ops", methods=["POST"])
@login_required
def ops():
    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not id:
        return AjaxFail('请选择要操作的账号')

    if act not in ['remove', 'recover'] :
        return AjaxFail(msg='操作有误，请重试')

    user_info = User.query.filter_by(uid=id).first()
    if not user_info:
        return AjaxFail('指定账号不存在')

    if act == "remove":
        user_info.status = 0
    elif act == "recover":
        user_info.status = 1

    if user_info and user_info.uid == 1:
        return AjaxFail('该用户super账号，不准操作')

    user_info.updated_time = get_current_date()
    with db.auto_commit():
        user_info

    if user_info.uid == current_user.uid and user_info.status == 0:
        logout_user()
    return AjaxSuccess()






