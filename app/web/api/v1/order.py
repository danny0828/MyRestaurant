"""
 Created by Danny on 2018/12/12
"""
from app.libs.redprint import Redprint
from flask import jsonify, request, g, current_app
from app.libs.token_auth import auth
import json, decimal
from app.models.base import db
from app.models.food.food import Food
from app.models.member.member_cart import MemberCart
from app.models.pay.pay_order import PayOrder
from app.models.member.member_auth_bind import MemberAuthBind
from app.models.member.member_address import MemberAddress
from app.libs.error_code import AuthFailed, ParameterException, Success
from app.libs.url_manager import UrlManager
from app.libs.pay.pay_service import PayService
from app.libs.pay.wechat_service import WeChatService
from app.validators.forms import PayForm, OrderOpsForm, OrderCreateForm
from app.libs.helper import get_current_date
__author__ = 'Danny'

api = Redprint('order')


@api.route("/info", methods=["POST"])
@auth.login_required
def order_info():
    req = request.get_json(silent=True)
    params_goods = req['goods'] if 'goods' in req else None
    member_info = g.user
    if not member_info:
        return AuthFailed('请先登录')
    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads(params_goods)

    food_dic = {}
    for item in params_goods_list:
        food_dic[item['id']] = item['number']

    food_ids = food_dic.keys()
    food_list = Food.query.filter(Food.id.in_(food_ids)).all()
    data_food_list = []
    yun_price = pay_price = decimal.Decimal(0.00)
    if food_list:
        for item in food_list:
            tmp_data = {
                "id": item.id,
                "name": item.name,
                "price": str(item.price),
                'pic_url': UrlManager.build_image_url(item.main_image),
                'number': food_dic[item.id]
            }
            pay_price = pay_price + item.price * int(food_dic[item.id])
            data_food_list.append(tmp_data)

    address_info = MemberAddress.query.filter_by(is_default=1, member_id=member_info.uid,
                                                 status=1).first()
    default_address = ''
    if address_info:
        default_address = {
            "id": address_info.id,
            "name": address_info.nickname,
            "mobile": address_info.mobile,
            "address": "%s%s%s%s" % (address_info.province_str, address_info.city_str,
                                     address_info.area_str, address_info.address)
        }
    resp = {}
    resp['food_list'] = data_food_list
    resp['pay_price'] = str(pay_price)
    resp['yun_price'] = str(yun_price)
    resp['total_price'] = str(pay_price + yun_price)
    resp['default_address'] = default_address
    return jsonify(resp)


@api.route("/create", methods=["POST"])
@auth.login_required
def order_create():
    member_info = g.user
    if not member_info:
        return AuthFailed('请先登录')
    form = OrderCreateForm().validate_for_api()

    items = []
    if form.goods:
        items = json.loads(form.goods.data)

    if len(items) < 1:
        return ParameterException('下单失败：没有选择商品')

    address_info = MemberAddress.query.filter_by(id=form.express_address_id.data).first()
    if not address_info or not address_info.status:
        return ParameterException('下单失败：快递地址不对')

    target = PayService()
    params = {
        'note': form.note.data,
        'express_address_id': address_info.id,
        'express_info': {
            'mobile': address_info.mobile,
            'nickname': address_info.nickname,
            "address": "%s%s%s%s" % (address_info.province_str, address_info.city_str,
                                     address_info.area_str, address_info.address)
        }
    }
    resp = target.create_order(member_info.uid, items, params)
    # 如果是来源购物车的，下单成功将下单的商品去掉
    if form.type.data == "cart":
        MemberCart.delete_item(member_info.uid, items)

    return jsonify(resp)


@api.route("/pay", methods=["POST"])
@auth.login_required
def order_pay():
    member_info = g.user
    form = PayForm().validate_for_api()
    order_sn = form.order_sn.data
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn,
                                              member_id=member_info.uid).first()
    if not pay_order_info:
        return ParameterException('系统繁忙。请稍后再试')

    member_auth_bind = MemberAuthBind.query.filter_by(member_id=member_info.uid).first()
    if not member_auth_bind:
        return ParameterException('系统繁忙。请稍后再试')

    config_mina = current_app.config['MINA_APP']
    notify_url = current_app.config['APP']['domain'] + config_mina['callback_url']

    target_wechat = WeChatService(merchant_key=config_mina['merchant_key'])

    # https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=9_1&index=1
    data = {
        'appid': config_mina['appid'],
        'mch_id': config_mina['mch_id'],
        'nonce_str': target_wechat.get_nonce_str(),
        'body': '订餐',                                    # 商品描述
        'out_trade_no': pay_order_info.order_sn,           # 商户订单号
        'total_fee': int(pay_order_info.total_price * 100),
        'notify_url': notify_url,
        'trade_type': 'JSAPI',
        'openid': member_auth_bind.openid
    }

    pay_info = target_wechat.get_pay_info(pay_data=data)

    # 保存prepay_id为了后面发模板消息
    pay_order_info.prepay_id = pay_info['prepay_id']
    with db.auto_commit():
        pay_order_info

    resp = {}
    resp['pay_info'] = pay_info
    return jsonify(resp)


# https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=9_7&index=8
@api.route("/callback", methods=["POST"])
def order_callback():
    result_data = {
        'return_code': 'SUCCESS',
        'return_msg': 'OK'
    }
    header = {'Content-Type': 'application/xml'}
    config_mina = current_app.config['MINA_APP']
    target_wechat = WeChatService(merchant_key=config_mina['merchant_key'])
    callback_data = target_wechat.xml_to_dict(request.data)
    current_app.logger.info(callback_data)
    sign = callback_data['sign']
    callback_data.pop('sign')
    gene_sign = target_wechat.create_sign(callback_data)
    current_app.logger.info(gene_sign)
    if sign != gene_sign:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header
    if callback_data['result_code'] != 'SUCCESS':
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    order_sn = callback_data['out_trade_no']
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if int(pay_order_info.total_price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if pay_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header

    target_pay = PayService()
    target_pay.order_success(pay_order_id=pay_order_info.id,
                             params={"pay_sn": callback_data['transaction_id']})
    # 将微信回调的结果记录
    target_pay.add_pay_callback_data(pay_order_id=pay_order_info.id, data=request.data)
    return target_wechat.dict_to_xml(result_data), header


@api.route("/ops", methods=["POST"])
@auth.login_required
def order_ops():
    member_info = g.user
    form = OrderOpsForm().validate_for_api()
    order_sn = form.order_sn.data
    act = form.act.data
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.uid).first()
    if not pay_order_info:
        return ParameterException('系统繁忙。请稍后再试')

    if act == "cancel":
        target_pay = PayService()
        ret = target_pay.close_order(pay_order_id=pay_order_info.id)
        if not ret:
            return ParameterException('系统繁忙。请稍后再试')
    elif act == "confirm":
        pay_order_info.express_status = 1
        pay_order_info.updated_time = get_current_date()
        with db.auto_commit():
            pay_order_info

    return Success('操作成功')








