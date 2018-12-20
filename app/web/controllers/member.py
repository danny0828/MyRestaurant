"""
 Created by Danny on 2018/11/28
"""
from flask import render_template, request, current_app, redirect
from app.web import member_bp
from app.models.member.member import Member
from app.libs.helper import i_pagination
from app.view_models.member import MembersViewModel, MemberViewModel
from app.libs.url_manager import UrlManager
from app.libs.error_code import AjaxFail, AjaxSuccess
from app.libs.helper import get_current_date
from app.models.base import db
from flask_login import login_required
__author__ = 'Danny'


@member_bp.route("/index")
@login_required
def index():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = Member.query

    if 'mix_kw' in req:
        query = query.filter(Member.nickname.ilike("%{0}%".format(req['mix_kw'])))

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(Member.status == int(req['status']))

    page_params = {
        'total': query.count(),
        'page_size': current_app.config['PAGE_SIZE'],
        'page': page,
        'display': current_app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = i_pagination(page_params)
    offset = (page - 1) * current_app.config['PAGE_SIZE']
    member_list = query.order_by(Member.id.desc()).offset(offset).limit(
        current_app.config['PAGE_SIZE']).all()
    members = MembersViewModel(member_list)

    resp_data['list'] = members.members
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['status_mapping'] = current_app.config['STATUS_MAPPING']
    resp_data['current'] = 'index'
    return render_template("member/index.html", **resp_data)


@member_bp.route("/info")
@login_required
def info():
    resp_data = {}
    req = request.args
    m_id = int(req.get("id", 0))
    back_url = UrlManager.build_url("/member/index")
    if m_id < 1:
        return redirect(back_url)

    member_info = Member.query.filter_by(id=m_id).first()
    if not member_info:
        return redirect(back_url)

    # pay_order_list = PayOrder.query.filter_by( member_id = m_id ).filter( PayOrder.status.in_( [-8,1] ) )\
    #     .order_by( PayOrder.id.desc() ).all()
    # comment_list = MemberComments.query.filter_by( member_id = m_id ).order_by( MemberComments.id.desc() ).all()

    resp_data['info'] = MemberViewModel(member_info)
    # resp_data['pay_order_list'] = pay_order_list
    # resp_data['comment_list'] = comment_list
    resp_data['current'] = 'index'
    return render_template("member/info.html", **resp_data)


@member_bp.route("/set", methods=["GET", "POST"])
@login_required
def set():
    if request.method == "GET":
        resp_data = {}
        req = request.args
        m_id = int(req.get("id", 0))
        back_url = UrlManager.build_url("/member/index")
        if m_id < 1:
            return redirect(back_url)

        member_info = Member.query.filter_by(id=m_id).first()
        if not member_info:
            return redirect(back_url)

        if member_info.status != 1:
            return redirect(back_url)

        resp_data['info'] = member_info
        resp_data['current'] = 'index'
        return render_template("member/set.html", **resp_data)

    req = request.values
    m_id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    if nickname is None or len(nickname) < 1:
        return AjaxFail('请输入符合规范的姓名')

    member_info = Member.query.filter_by(id=m_id).first()
    if not member_info:
        return AjaxFail('指定会员不存在')

    member_info.nickname = nickname
    member_info.updated_time = get_current_date()

    with db.auto_commit():
        member_info
    return AjaxSuccess()


@member_bp.route("/comment")
@login_required
def comment():
    return render_template("member/comment.html")


@member_bp.route("/ops", methods=["POST"])
@login_required
def ops():
    req = request.values

    m_id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''

    if not m_id:
        return AjaxFail('请选择要操作的账号')

    if act not in ['remove', 'recover']:
        return AjaxFail('操作有误，请重试')

    member_info = Member.query.filter_by(id=m_id).first()
    if not member_info:
        return AjaxFail('指定会员不存在')

    if act == "remove":
        member_info.status = 0
    elif act == "recover":
        member_info.status = 1

    member_info.updated_time = get_current_date()
    with db.auto_commit():
        member_info
    return AjaxSuccess()









