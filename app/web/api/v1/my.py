"""
 Created by Danny on 2018/12/13
"""
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.validators.forms import MyOrderForm, CommentForm, AddressForm, OpsForm, IdForm, PayForm
from app.models.pay.pay_order import PayOrder
from app.models.pay.pay_order_item import PayOrderItem
from app.models.food.food import Food
from app.models.member.member_comments import MemberComments
from app.models.base import db
from flask import g, jsonify
from app.libs.enums import OrderStatusEnum
from app.libs.helper import select_filter_obj, get_dict_filter_field, get_current_date
from app.libs.url_manager import UrlManager
from app.libs.error_code import Success, ParameterException
from app.models.member.member_address import MemberAddress
import json, datetime
__author__ = 'Danny'

api = Redprint('my')


@api.route("/order", methods=['POST'])
@auth.login_required
def my_order_list():
    member_info = g.user
    form = MyOrderForm().validate_for_api()
    status = form.status.data
    query = PayOrder.query.filter_by(member_id=member_info.uid)

    if status == OrderStatusEnum.WAIT:  # 等待付款
        query = query.filter(PayOrder.status == -8)
    elif status == OrderStatusEnum.SEND:  # 待发货
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == -7,
                             PayOrder.comment_status == 0)
    elif status == OrderStatusEnum.CONFIRM:  # 待确认
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == -6,
                             PayOrder.comment_status == 0)
    elif status == OrderStatusEnum.SAY:  # 待评价
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == 1,
                             PayOrder.comment_status == 0)
    elif status == OrderStatusEnum.OK:  # 已完成
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == 1,
                             PayOrder.comment_status == 1)
    else:
        query = query.filter(PayOrder.status == 0)

    pay_order_list = query.order_by(PayOrder.id.desc()).all()
    data_pay_order_list = []
    if pay_order_list:
        pay_order_ids = select_filter_obj(pay_order_list, "id")
        pay_order_item_list = PayOrderItem.query.filter(
            PayOrderItem.pay_order_id.in_(pay_order_ids)).all()
        food_ids = select_filter_obj(pay_order_item_list, "food_id")
        food_map = get_dict_filter_field(Food, Food.id, "id", food_ids)
        pay_order_item_map = {}
        if pay_order_item_list:
            for item in pay_order_item_list:
                if item.pay_order_id not in pay_order_item_map:
                    pay_order_item_map[item.pay_order_id] = []

                tmp_food_info = food_map[item.food_id]
                pay_order_item_map[item.pay_order_id].append({
                    'id': item.id,
                    'food_id': item.food_id,
                    'quantity': item.quantity,
                    'price': str(item.price),
                    'pic_url': UrlManager.build_image_url(tmp_food_info.main_image),
                    'name': tmp_food_info.name
                })

        for item in pay_order_list:
            tmp_data = {
                'status': item.pay_status,
                'status_desc': item.status_desc,
                'date': item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                'order_number': item.order_number,
                'order_sn': item.order_sn,
                'note': item.note,
                'total_price': str(item.total_price),
                'goods_list': pay_order_item_map[item.id]
            }

            data_pay_order_list.append(tmp_data)
    resp = {}
    resp['pay_order_list'] = data_pay_order_list
    return jsonify(resp)


@api.route("/comment/add", methods=["POST"])
@auth.login_required
def my_comment_add():
    member_info = g.user
    form = CommentForm().validate_for_api()
    order_sn = form.order_sn.data
    score = form.score.data
    content = form.content.data

    pay_order_info = PayOrder.query.filter_by(member_id=member_info.uid, order_sn=order_sn).first()
    if not pay_order_info:
        return ParameterException('系统繁忙，请稍后再试')

    if pay_order_info.comment_status:
        return ParameterException('已经评价过了')

    pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
    food_ids = select_filter_obj( pay_order_items, "food_id")
    tmp_food_ids_str = '_'.join(str(s) for s in food_ids if s not in [None])
    model_comment = MemberComments()
    model_comment.food_ids = "_%s_" % tmp_food_ids_str
    model_comment.member_id = member_info.uid
    model_comment.pay_order_id = pay_order_info.id
    model_comment.score = score
    model_comment.content = content
    with db.auto_commit():
        db.session.add(model_comment)

    pay_order_info.comment_status = 1
    pay_order_info.updated_time = get_current_date()
    with db.auto_commit():
        pay_order_info
    return Success()


@api.route("/comment/list")
@auth.login_required
def my_comment_list():
    member_info = g.user
    comment_list = MemberComments.query.filter_by(member_id=member_info.uid)\
        .order_by(MemberComments.id.desc()).all()
    data_comment_list = []
    if comment_list:
        pay_order_ids = select_filter_obj(comment_list, "pay_order_id")
        pay_order_map = get_dict_filter_field(PayOrder, PayOrder.id, "id", pay_order_ids)
        for item in comment_list:
            tmp_pay_order_info = pay_order_map[item.pay_order_id]
            tmp_data = {
                "date": item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "content": item.content,
                "order_number": tmp_pay_order_info.order_number
            }
            data_comment_list.append(tmp_data)
    return jsonify(data_comment_list)


@api.route("/address/index")
@auth.login_required
def my_address_list():
    member_info = g.user
    list = MemberAddress.query.filter_by(status=1, member_id=member_info.uid)\
        .order_by(MemberAddress.id.desc()).all()
    return jsonify(list)


@api.route("/address/set", methods=["POST"])
@auth.login_required
def my_address_set():
    form = AddressForm().validate_for_api()
    member_info = g.user

    if not member_info:
        return ParameterException('系统繁忙，请稍后再试')

    address_info = MemberAddress.query.filter_by(id=form.id.data, member_id=member_info.uid).first()
    if address_info:
        model_address = address_info
    else:
        default_address_count = MemberAddress.query.filter_by(is_default=1, member_id=member_info.uid, status=1).count()
        model_address = MemberAddress()
        model_address.member_id = member_info.uid
        model_address.is_default = 1 if default_address_count == 0 else 0
        model_address.created_time = get_current_date()

    model_address.nickname = form.nickname.data
    model_address.mobile = form.mobile.data
    model_address.address = form.address.data
    model_address.province_id = form.province_id.data
    model_address.province_str = form.province_str.data
    model_address.city_id = form.city_id.data
    model_address.city_str = form.city_str.data
    model_address.area_id = form.district_id.data
    model_address.area_str = form.district_str.data
    model_address.updated_time = get_current_date()
    with db.auto_commit():
        db.session.add(model_address)
    return Success()


@api.route("/address/ops", methods=["POST"])
@auth.login_required
def my_address_ops():
    form = OpsForm().validate_for_api()
    id = form.id.data
    act = form.act.data
    member_info = g.user

    address_info = MemberAddress.query.filter_by(id=id, member_id=member_info.uid).first()
    if not address_info:
        return ParameterException('系统繁忙，请稍后再试')

    if act == "del":
        address_info.status = 0
        address_info.updated_time = get_current_date()

    elif act == "default":
        MemberAddress.query.filter_by(member_id=member_info.uid)\
            .update({'is_default': 0})
        address_info.is_default = 1
        address_info.updated_time = get_current_date()
    with db.auto_commit():
        address_info
    return Success()


@api.route("/address/info", methods=['POST'])
@auth.login_required
def my_address_info():
    form = IdForm().validate_for_api()

    address_info = MemberAddress.query.filter_by(id=form.id.data).first_or_404()
    return jsonify(address_info)


@api.route("/order/info")
@auth.login_required
def my_order_info():
    form = PayForm().validate_for_api()
    member_info = g.user
    pay_order_info = PayOrder.query.filter_by(member_id=member_info.uid,
                                              order_sn=form.order_sn.data).first_or_404()

    express_info = {}
    if pay_order_info.express_info:
        express_info = json.loads(pay_order_info.express_info)

    tmp_deadline = pay_order_info.created_time + datetime.timedelta(minutes=30)
    info = {
        "order_sn": pay_order_info.order_sn,
        "status": pay_order_info.pay_status,
        "status_desc": pay_order_info.status_desc,
        "pay_price": str(pay_order_info.pay_price),
        "yun_price": str(pay_order_info.yun_price),
        "total_price": str(pay_order_info.total_price),
        "address": express_info,
        "goods": [],
        "deadline": tmp_deadline.strftime("%Y-%m-%d %H:%M")
    }

    pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
    if pay_order_items:
        food_ids = select_filter_obj( pay_order_items , "food_id")
        food_map = get_dict_filter_field(Food, Food.id, "id", food_ids)
        for item in pay_order_items:
            tmp_food_info = food_map[item.food_id]
            tmp_data = {
                "name": tmp_food_info.name,
                "price": str( item.price ),
                "unit": item.quantity,
                "pic_url": UrlManager.build_image_url(tmp_food_info.main_image),
            }
            info['goods'].append(tmp_data)
    return jsonify(info)





