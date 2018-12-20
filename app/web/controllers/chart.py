"""
 Created by Danny on 2018/12/19
"""
from app.web import chart_bp
from flask_login import login_required
import datetime
from app.libs.helper import get_format_date
from app.models.stat.stat_daily_site import StatDailySite
from flask import jsonify
__author__ = 'Danny'


@chart_bp.route("/dashboard")
@login_required
def dashboard():
    now = datetime.datetime.now()
    date_before_30days = now + datetime.timedelta(days=-30)
    date_from = get_format_date(date=date_before_30days, format="%Y-%m-%d")
    date_to = get_format_date(date=now, format="%Y-%m-%d")

    list = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()) \
        .all()

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    data = {
        "categories": [],
        "series": [
            {
                "name": "会员总数",
                "data": []
            },
            {
                "name": "订单总数",
                "data": []
            },
        ]
    }

    if list:
        for item in list:
            data['categories'].append(get_format_date(date=item.date, format="%Y-%m-%d"))
            data['series'][0]['data'].append(item.total_member_count)
            data['series'][1]['data'].append(item.total_order_count)

    resp['data'] = data
    return jsonify(resp)


@chart_bp.route("/finance")
@login_required
def finance():
    now = datetime.datetime.now()
    date_before_30days = now + datetime.timedelta(days=-30)
    date_from = get_format_date(date=date_before_30days, format="%Y-%m-%d")
    date_to = get_format_date(date=now, format="%Y-%m-%d")

    list = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()) \
        .all()

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    data = {
        "categories": [],
        "series": [
            {
                "name": "日营收报表",
                "data": []
            }
        ]
    }

    if list:
        for item in list:
            data['categories'].append(get_format_date(date=item.date, format="%Y-%m-%d"))
            data['series'][0]['data'].append(float(item.total_pay_money))

    resp['data'] = data
    return jsonify(resp)


@chart_bp.route("/share")
@login_required
def share():
    now = datetime.datetime.now()
    date_before_30days = now + datetime.timedelta(days=-30)
    date_from = get_format_date(date=date_before_30days, format="%Y-%m-%d")
    date_to = get_format_date(date=now, format="%Y-%m-%d")

    list = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()) \
        .all()

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    data = {
        "categories": [],
        "series": [
            {
                "name": "日分享",
                "data": []
            }
        ]
    }

    if list:
        for item in list:
            data['categories'].append(get_format_date(date=item.date, format="%Y-%m-%d"))
            data['series'][0]['data'].append(item.total_shared_count)

    resp['data'] = data
    return jsonify(resp)









