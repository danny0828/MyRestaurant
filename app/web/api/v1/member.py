"""
 Created by Danny on 2018/12/3
"""
from app.libs.redprint import Redprint
from flask import request, jsonify, current_app, g
from app.libs.member.member_service import MemberService
from app.models.member.member_auth_bind import MemberAuthBind
from app.libs.enums import ClientTypeEnum
from app.validators.forms import ClientForm, ShareForm
from app.models.member.member import Member
from app.models.member.member_cart import MemberCart
from app.libs.helper import get_current_date
from app.libs.error_code import ServerError, NotFound, AuthFailed, Success
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.models.base import db
from app.models.wx_share_history import WxShareHistory
from app.libs.token_auth import auth
__author__ = 'Danny'


api = Redprint('member')


@api.route('/login', methods=['POST'])
def login():
    form = ClientForm().validate_for_api()
    promise = {
        ClientTypeEnum.USER_MINA: __login_by_mina
    }
    identity = promise[form.type.data](form.account.data)
    return result_token(200, identity.id, auth=identity.auth)


@api.route("/check-bind", methods=["POST"])
def check_bind():
    form = ClientForm().validate_for_api()
    promise = {
        ClientTypeEnum.USER_MINA: __check_bind_by_mina
    }
    identity = promise[form.type.data](form.account.data)

    return result_token(201, identity.id, auth=identity.auth)


@api.route("/share", methods=["POST"])
@auth.login_required
def member_share():
    form = ShareForm().validate_for_api()
    # req = request.get_json(silent=True)
    # url = req['url'] if 'url' in req else ''
    member_info = g.user
    model_share = WxShareHistory()
    is_exist = model_share.query.filter_by(share_url=form.url.data, member_id=member_info.uid).first()
    if is_exist:
        return Success(msg='已经分享过了')
    if member_info:
        model_share.member_id = member_info.uid
    model_share.share_url = form.url.data
    model_share.created_time = get_current_date()
    with db.auto_commit():
        db.session.add(model_share)
    return Success(msg='分享成功')


@api.route("/auth", methods=["GET"])
@auth.login_required
def test_auth():
    return Success()


@api.route("/info")
@auth.login_required
def get_member_info():
    member = Member.query.get(g.user.uid)
    resp = {}
    resp['info'] = {
        "nickname": member.nickname,
        "avatar_url": member.avatar
    }
    return jsonify(resp)


def __check_bind_by_mina(code):
    openid = MemberService.get_wechat_openid(code)
    if openid is None:
        raise ServerError(msg='调用微信出错', error_code=2001)
    return check_member_bind(openid)


def __login_by_mina(code):
    openid = MemberService.get_wechat_openid(code)
    if openid is None:
        raise ServerError(msg='调用微信出错', error_code=2001)

    bind_info = check_member_bind(openid, 1)
    if not bind_info:
        req = request.json
        nickname = req['nickName'] if 'nickName' in req else ''
        sex = req['gender'] if 'gender' in req else 0
        avatar = req['avatarUrl'] if 'avatarUrl' in req else ''

        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.salt = MemberService.gene_salt()
        model_member.updated_time = model_member.created_time = get_current_date()
        with db.auto_commit():
            db.session.add(model_member)
        with db.auto_commit():
            model_bind = MemberAuthBind()
            model_bind.member_id = model_member.id
            model_bind.type = ClientTypeEnum.USER_MINA.value
            model_bind.openid = openid
            model_bind.extra = ''
            model_bind.updated_time = model_bind.created_time = get_current_date()
            db.session.add(model_bind)

        bind_info = model_member

    member_info = Member.query.filter_by(id=bind_info.id).first()
    return member_info


@api.route('/cart')
@auth.login_required
def cart_count():
    member_info = g.user
    cart_number = 0
    if member_info:
        cart_number = MemberCart.query.filter_by(member_id=member_info.uid).count()
    return jsonify(cart_number)


def generate_auth_token(uid, ac_type, scope=None,
                        expiration=7200):
    """生成令牌"""
    s = Serializer(current_app.config['SECRET_KEY'],
                   expires_in=expiration)
    return s.dumps({
        'uid': uid,
        'type': ac_type,
        'scope': scope
    })


def result_token(status_code, uid, ac_type=200, auth=0):
    scope = 'AdminScope' if auth == 1 else 'UserScope'
    expiration = current_app.config['TOKEN_EXPIRATION']
    token = generate_auth_token(uid,
                                ac_type,
                                scope,
                                expiration)
    t = {
        'token': token.decode('ascii')
    }
    # token = "%s#%s"%( MemberService.geneAuthCode( member_info ),member_info.id )
    # resp['data'] = {'token': token}
    return jsonify(t), status_code


def check_member_bind(openid, reg=0):
    bind_info = MemberAuthBind.query.filter_by(openid=openid,
                                               type=ClientTypeEnum.USER_MINA.value).first()

    if not bind_info:
        if reg == 0:
            raise NotFound(msg='未绑定', error_code=2002)
        else:
            return

    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    if not member_info:
        if reg == 0:
            raise NotFound(msg='未查询到绑定信息', error_code=2003)

    if member_info.status == 0:
        raise AuthFailed(msg='账户被禁用', error_code=2004)
    return member_info









