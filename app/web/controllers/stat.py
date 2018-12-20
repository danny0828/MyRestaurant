"""
 Created by Danny on 2018/11/28
"""
from flask import render_template, request, current_app
from app.web import stat_bp
import datetime
from app.libs.helper import get_format_date, i_pagination, \
    get_dict_filter_field, select_filter_obj
from app.models.stat.stat_daily_site import StatDailySite
from app.models.stat.stat_daily_member import StatDailyMember
from app.models.stat.stat_daily_food import StatDailyFood
from app.models.food.food import Food
from app.models.member.member import Member
from flask_login import login_required
__author__ = 'Danny'


@stat_bp.route("/index")
@login_required
def index():
    now = datetime.datetime.now()
    date_before_30days = now + datetime.timedelta(days=-30)
    default_date_from = get_format_date(date=date_before_30days, format="%Y-%m-%d")
    default_date_to = get_format_date(date=now, format="%Y-%m-%d")

    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    date_from = req['date_from'] if 'date_from' in req else default_date_from
    date_to = req['date_to'] if 'date_to' in req else default_date_to
    query = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to)

    page_params = {
        'total': query.count(),
        'page_size': current_app.config['PAGE_SIZE'],
        'page': page,
        'display': current_app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = i_pagination(page_params)
    offset = (page - 1) * current_app.config['PAGE_SIZE']

    list = query.order_by(StatDailySite.id.desc()).offset(
        offset).limit(current_app.config['PAGE_SIZE']).all()
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['current'] = 'index'
    resp_data['search_con'] = {
        'date_from': date_from,
        'date_to': date_to
    }
    return render_template("stat/index.html", **resp_data)


@stat_bp.route("/food")
@login_required
def food():
    now = datetime.datetime.now()
    date_before_30days = now + datetime.timedelta(days=-30)
    default_date_from = get_format_date(date=date_before_30days, format="%Y-%m-%d")
    default_date_to = get_format_date(date=now, format="%Y-%m-%d")

    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    date_from = req['date_from'] if 'date_from' in req else default_date_from
    date_to = req['date_to'] if 'date_to' in req else default_date_to
    query = StatDailyFood.query.filter(StatDailyFood.date >= date_from) \
        .filter(StatDailyFood.date <= date_to)

    page_params = {
        'total': query.count(),
        'page_size': current_app.config['PAGE_SIZE'],
        'page': page,
        'display': current_app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = i_pagination(page_params)
    offset = (page - 1) * current_app.config['PAGE_SIZE']

    list = query.order_by(StatDailyFood.id.desc()).offset(offset).limit(
        current_app.config['PAGE_SIZE']).all()
    date_list = []
    if list:
        food_map = get_dict_filter_field(Food, Food.id, "id", select_filter_obj(
            list, "food_id"))
        for item in list:
            tmp_food_info = food_map[item.food_id] if item.food_id in food_map else {}
            tmp_data = {
                "date": item.date,
                "total_count": item.total_count,
                "total_pay_money": item.total_pay_money,
                'food_info': tmp_food_info
            }
            date_list.append(tmp_data)

    resp_data['list'] = date_list
    resp_data['pages'] = pages
    resp_data['current'] = 'food'
    resp_data['search_con'] = {
        'date_from': date_from,
        'date_to': date_to
    }
    return render_template("stat/food.html", **resp_data)


@stat_bp.route("/member")
@login_required
def member():
    now = datetime.datetime.now()
    date_before_30days = now + datetime.timedelta(days=-30)
    default_date_from = get_format_date(date=date_before_30days, format="%Y-%m-%d")
    default_date_to = get_format_date(date=now, format="%Y-%m-%d")

    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    date_from = req['date_from'] if 'date_from' in req else default_date_from
    date_to = req['date_to'] if 'date_to' in req else default_date_to
    query = StatDailyMember.query.filter(StatDailyMember.date >= date_from) \
        .filter(StatDailyMember.date <= date_to)

    page_params = {
        'total': query.count(),
        'page_size': current_app.config['PAGE_SIZE'],
        'page': page,
        'display': current_app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = i_pagination(page_params)
    offset = (page - 1) * current_app.config['PAGE_SIZE']

    list = query.order_by(StatDailyMember.id.desc()).offset(
        offset).limit(current_app.config['PAGE_SIZE']).all()
    date_list = []
    if list:
        member_map = get_dict_filter_field(Member, Member.id, "id",
                                           select_filter_obj(list, "member_id"))
        for item in list:
            tmp_member_info = member_map[item.member_id] \
                if item.member_id in member_map else {}
            tmp_data = {
                "date": item.date,
                "total_pay_money": item.total_pay_money,
                "total_shared_count": item.total_shared_count,
                'member_info': tmp_member_info
            }
            date_list.append(tmp_data)

    resp_data['list'] = date_list
    resp_data['pages'] = pages
    resp_data['current'] = 'member'
    resp_data['search_con'] = {
        'date_from': date_from,
        'date_to': date_to
    }
    return render_template("stat/member.html", **resp_data)


@stat_bp.route("/share")
@login_required
def share():
    now = datetime.datetime.now()
    date_before_30days = now + datetime.timedelta(days=-30)
    default_date_from = get_format_date(date=date_before_30days, format="%Y-%m-%d")
    default_date_to = get_format_date(date=now, format="%Y-%m-%d")

    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    date_from = req['date_from'] if 'date_from' in req else default_date_from
    date_to = req['date_to'] if 'date_to' in req else default_date_to
    query = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to)

    page_params = {
        'total': query.count(),
        'page_size': current_app.config['PAGE_SIZE'],
        'page': page,
        'display': current_app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = i_pagination(page_params)
    offset = (page - 1) * current_app.config['PAGE_SIZE']

    list = query.order_by(StatDailySite.id.desc()).offset(offset).limit(current_app.config['PAGE_SIZE']).all()
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['current'] = 'share'
    resp_data['search_con'] = {
        'date_from': date_from,
        'date_to': date_to
    }
    return render_template("stat/share.html", **resp_data)









