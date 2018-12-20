"""
 Created by Danny on 2018/12/11
"""
from app.libs.redprint import Redprint
from app.libs.error_code import Success, NotFound, ParameterException, AuthFailed
from app.validators.forms import CartForm
from flask import g, jsonify, request
from app.models.food.food import Food
from app.models.member.member_cart import MemberCart
from app.libs.token_auth import auth
from app.libs.helper import select_filter_obj, get_dict_filter_field
from app.libs.url_manager import UrlManager
import json
__author__ = 'Danny'

api = Redprint('cart')


@api.route("/index")
@auth.login_required
def cart_index():
    member_info = g.user
    if not member_info:
        return AuthFailed('请先登录')
    cart_list = MemberCart.query.filter_by(member_id=member_info.uid).all()
    data_cart_list = []
    resp = {}
    if cart_list:
        food_ids = select_filter_obj(cart_list, "food_id")
        food_map = get_dict_filter_field(Food, Food.id, "id", food_ids)
        for item in cart_list:
            tmp_food_info = food_map[item.food_id]
            tmp_data = {
                "id": item.id,
                "number": item.quantity,
                "food_id": item.food_id,
                "name": tmp_food_info.name,
                "price": str(tmp_food_info.price),
                "pic_url": UrlManager.build_image_url(tmp_food_info.main_image),
                "active": True
            }
            data_cart_list.append(tmp_data)

    resp['data'] = data_cart_list
    return jsonify(resp)


@api.route('/set', methods=["POST"])
@auth.login_required
def set_cart():
    form = CartForm().validate_for_api()
    # req = request.values
    # food_id = int(req['id']) if 'id' in req else 0
    # number = int(req['number']) if 'number' in req else 0
    # if food_id < 1 or number < 1:
    #     return jsonify(resp)

    member_info = g.user
    if not member_info:
        return AuthFailed('请先登录')

    food_info = Food.query.filter_by(id=form.id.data).first()
    if not food_info:
        return NotFound('添加购物车失败-1')

    if food_info.stock < form.number.data:
        return ParameterException('添加购物车失败,库存不足')

    ret = MemberCart.set_items(member_id=member_info.uid, food_id=food_info.id, number=form.number.data)
    if not ret:
        return ParameterException('添加购物车失败-2')
    return Success('更新购物车成功')


@api.route("/del", methods=["POST"])
@auth.login_required
def del_cart():
    req = request.get_json(silent=True)
    params_goods = req['goods'] if 'goods' in req else None

    items = []
    if params_goods:
        items = json.loads(params_goods)
    if not items or len(items) < 1:
        return ParameterException('没有相关参数')

    member_info = g.user
    if not member_info:
        return AuthFailed('请先登录')

    ret = MemberCart.delete_item(member_id=member_info.uid, items=items)
    if not ret:
        return ParameterException('删除购物车失败')
    return Success('删除购物车成功')
