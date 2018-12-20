"""
 Created by Danny on 2018/11/28
"""
from app.web import web
from flask_login import login_required
from flask import render_template
import datetime
from app.libs.helper import get_format_date
from app.models.stat.stat_daily_site import StatDailySite
__author__ = 'Danny'


@web.route('/')
@login_required
def index():
    # current_user = g.current_user
    resp_data = {
        'data': {
            'finance': {
                'today': 0,
                'month': 0
            },
            'member': {
                'today_new': 0,
                'month_new': 0,
                'total': 0
            },
            'order': {
                'today': 0,
                'month': 0
            },
            'shared': {
                'today': 0,
                'month': 0
            },
        }
    }

    now = datetime.datetime.now()
    date_before_30days = now + datetime.timedelta(days=-30)
    date_from = get_format_date(date=date_before_30days, format="%Y-%m-%d")
    date_to = get_format_date(date=now, format="%Y-%m-%d")

    list = StatDailySite.query.filter(StatDailySite.date >= date_from)\
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc())\
        .all()
    data = resp_data['data']
    if list:

        for item in list:
            data['finance']['month'] += item.total_pay_money
            data['member']['month_new'] += item.total_new_member_count
            data['member']['total'] = item.total_member_count
            data['order']['month'] += item.total_order_count
            data['shared']['month'] += item.total_shared_count
            if get_format_date(date=item.date, format="%Y-%m-%d") == date_to:
                data['finance']['today'] = item.total_pay_money
                data['member']['today_new'] = item.total_new_member_count
                data['order']['today'] = item.total_order_count
                data['shared']['today'] = item.total_shared_count

    return render_template("index/index.html", **resp_data)


@web.route('/1')
def index1():
    return 'web index 666666'









