"""
 Created by Danny on 2018/11/28
"""
from app.web import finance_bp
from flask import render_template, request, current_app, redirect
from flask_login import login_required
from app.models.pay.pay_order import PayOrder
from app.models.pay.pay_order_item import PayOrderItem
from app.models.food.food import Food
from app.models.base import db
from app.models.member.member import Member
from app.libs.helper import i_pagination, select_filter_obj,\
    get_dict_list_filter_field, get_dict_filter_field, get_current_date
from sqlalchemy import func
from app.libs.url_manager import UrlManager
import json
from app.libs.error_code import AjaxSuccess, AjaxFail
__author__ = 'Danny'


@finance_bp.route("/index")
@login_required
def index():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1

    query = PayOrder.query

    if 'status' in req and int(req['status']) != -1:
        query = query.filter(PayOrder.status == int(req['status']))

    page_params = {
        'total': query.count(),
        'page_size': current_app.config['PAGE_SIZE'],
        'page': page,
        'display': current_app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = i_pagination(page_params)
    offset = (page - 1) * current_app.config['PAGE_SIZE']
    pay_list = query.order_by(PayOrder.id.desc()).offset(offset).limit(current_app.config['PAGE_SIZE']).all()
    data_list = []
    if pay_list:
        pay_order_ids = select_filter_obj( pay_list,"id" )
        pay_order_items_map = get_dict_list_filter_field(PayOrderItem,
                                                         PayOrderItem.pay_order_id,
                                                         "pay_order_id", pay_order_ids)

        food_mapping = {}
        if pay_order_items_map:
            food_ids = []
            for item in pay_order_items_map:
                tmp_food_ids = select_filter_obj(pay_order_items_map[item], "food_id")
                tmp_food_ids = {}.fromkeys(tmp_food_ids).keys()
                food_ids = food_ids + list(tmp_food_ids)

            #food_ids里面会有重复的，要去重
            food_mapping = get_dict_filter_field(Food, Food.id, "id", food_ids)

        for item in pay_list:
            tmp_data = {
                "id": item.id,
                "status_desc": item.status_desc,
                "order_number": item.order_number,
                "price": item.total_price,
                "pay_time": item.pay_time,
                "created_time": item.created_time.strftime("%Y%m%d%H%M%S")
            }
            tmp_foods = []
            tmp_order_items = pay_order_items_map[item.id]
            for tmp_order_item in tmp_order_items:
                tmp_food_info = food_mapping[tmp_order_item.food_id]
                tmp_foods.append({
                    'name': tmp_food_info.name,
                    'quantity': tmp_order_item.quantity
                })

            tmp_data['foods'] = tmp_foods
            data_list.append(tmp_data)

    resp_data['list'] = data_list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['pay_status_mapping'] = current_app.config['PAY_STATUS_MAPPING']
    resp_data['current'] = 'index'

    return render_template("finance/index.html", **resp_data)


@finance_bp.route("/pay-info")
@login_required
def pay_info():
    resp_data = {}
    req = request.values
    id = int(req['id']) if 'id' in req else 0

    back_url = UrlManager.build_url("/finance/index")

    if id < 1:
        return redirect(back_url)

    pay_order_info = PayOrder.query.filter_by( id = id ).first()
    if not pay_order_info:
        return redirect(back_url)

    member_info = Member.query.filter_by(id=pay_order_info.member_id).first()
    if not member_info:
        return redirect(back_url)

    order_item_list = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
    data_order_item_list = []
    if order_item_list:
        food_map = get_dict_filter_field(Food, Food.id, "id", select_filter_obj(order_item_list, "food_id"))
        for item in order_item_list:
            tmp_food_info = food_map[item.food_id]
            tmp_data = {
                "quantity": item.quantity,
                "price": item.price,
                "name": tmp_food_info.name
            }
            data_order_item_list.append(tmp_data)

    address_info = {}
    if pay_order_info.express_info:
        address_info = json.loads(pay_order_info.express_info)

    resp_data['pay_order_info'] = pay_order_info
    resp_data['pay_order_items'] = data_order_item_list
    resp_data['member_info'] = member_info
    resp_data['address_info'] = address_info
    resp_data['current'] = 'index'
    return render_template("finance/pay_info.html", **resp_data)


@finance_bp.route("/account")
@login_required
def account():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = PayOrder.query.filter_by(status=1)

    page_params = {
        'total': query.count(),
        'page_size': current_app.config['PAGE_SIZE'],
        'page': page,
        'display': current_app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = i_pagination(page_params)
    offset = (page - 1) * current_app.config['PAGE_SIZE']
    list = query.order_by(PayOrder.id.desc()).offset(offset).limit(current_app.config['PAGE_SIZE']).all()

    stat_info = db.session.query(PayOrder, func.sum(PayOrder.total_price).label("total"))\
        .filter(PayOrder.status == 1).first()

    current_app.logger.info(stat_info)
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['total_money'] = stat_info[1] if stat_info[1] else 0.00
    resp_data['current'] = 'account'
    return render_template("finance/account.html", **resp_data)


@finance_bp.route("/ops", methods=["POST"])
@login_required
def order_ops():
    req = request.values
    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    pay_order_info = PayOrder.query.filter_by(id=id).first()
    if not pay_order_info:
        return AjaxFail('系统繁忙。请稍后再试')

    if act == "express":
        pay_order_info.express_status = -6
        pay_order_info.updated_time = get_current_date()
        with db.auto_commit():
            pay_order_info

    return AjaxSuccess()









