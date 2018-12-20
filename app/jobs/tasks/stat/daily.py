"""
 Created by Danny on 2018/12/18
"""
from app.libs.helper import get_format_date, get_current_date
from app.app import app
from app.models.member.member import Member
from app.models.stat.stat_daily_member import StatDailyMember
from app.models.stat.stat_daily_food import StatDailyFood
from app.models.stat.stat_daily_site import StatDailySite
from app.models.pay.pay_order import PayOrder
from app.models.wx_share_history import WxShareHistory
from app.models.food.food_sale_change_log import FoodSaleChangeLog
from app.models.base import db
from sqlalchemy import func
import random

__author__ = 'Danny'


# python manager.py runjob -m stat/daily -a member|food|site -p 2018-08-28
class JobTask:
    def __init__(self):
        pass

    def run(self, params):
        act = params['act'] if 'act' in params else ''
        date = params['param'][0] if params['param'] and len(params['param']) else \
            get_format_date(format="%Y-%m-%d")
        if not act:
            return

        date_from = date + " 00:00:00"
        date_to = date + " 23:59:59"
        func_params = {
            'act': act,
            'date': date,
            'date_from': date_from,
            'date_to': date_to
        }
        if act == "member":
            self.stat_member(func_params)
        elif act == "food":
            self.stat_food(func_params)
        elif act == "site":
            self.stat_site(func_params)
        elif act == "test":
            self.test()

        app.logger.info("it's over~~")
        return

    # 会员统计
    def stat_member(self, params):
        act = params['act']
        date = params['date']
        date_from = params['date_from']
        date_to = params['date_to']
        app.logger.info("act:{0},from:{1},to:{2}".format(act, date_from, date_to))

        member_list = Member.query.all()
        if not member_list:
            app.logger.info("no member list")
            return

        for member_info in member_list:
            tmp_stat_member = StatDailyMember.query.filter_by(
                date=date, member_id=member_info.id).first()
            if tmp_stat_member:
                tmp_model_stat_member = tmp_stat_member
            else:
                tmp_model_stat_member = StatDailyMember()
                tmp_model_stat_member.date = date
                tmp_model_stat_member.member_id = member_info.id
                tmp_model_stat_member.created_time = get_current_date()

            tmp_stat_pay = db.session.query(func.sum(
                PayOrder.total_price).label("total_pay_money")) \
                .filter(PayOrder.member_id == member_info.id, PayOrder.status == 1) \
                .filter(PayOrder.created_time >= date_from,
                        PayOrder.created_time <= date_to).first()
            tmp_stat_share_count = WxShareHistory.query.filter(
                PayOrder.member_id == member_info.id) \
                .filter(PayOrder.created_time >= date_from,
                        PayOrder.created_time <= date_to).count()

            tmp_model_stat_member.total_shared_count = tmp_stat_share_count
            tmp_model_stat_member.total_pay_money = tmp_stat_pay[0] if tmp_stat_pay[0] else 0.00

            # 模拟数据
            tmp_model_stat_member.total_shared_count = random.randint(50, 100)
            if tmp_model_stat_member.total_pay_money == 0:
                tmp_model_stat_member.total_pay_money = random.randint(1000, 1010)

            tmp_model_stat_member.updated_time = get_current_date()
            with db.auto_commit():
                db.session.add(tmp_model_stat_member)

        return

    # Food统计
    def stat_food(self, params):
        act = params['act']
        date = params['date']
        date_from = params['date_from']
        date_to = params['date_to']
        app.logger.info("act:{0},from:{1},to:{2}".format(act, date_from, date_to))

        stat_food_list = db.session.query(FoodSaleChangeLog.food_id, func.sum(
            FoodSaleChangeLog.quantity).label("total_count"),
            func.sum(FoodSaleChangeLog.price).label("total_pay_money")) \
            .filter(FoodSaleChangeLog.created_time >= date_from,
                    FoodSaleChangeLog.created_time <= date_to)\
            .group_by(FoodSaleChangeLog.food_id).all()

        if not stat_food_list:
            app.logger.info("no data")
            return

        for item in stat_food_list:
            tmp_food_id = item[0]
            tmp_stat_food = StatDailyFood.query.filter_by(
                date=date, food_id=tmp_food_id).first()
            if tmp_stat_food:
                tmp_model_stat_food = tmp_stat_food
            else:
                tmp_model_stat_food = StatDailyFood()
                tmp_model_stat_food.date = date
                tmp_model_stat_food.food_id = tmp_food_id
                tmp_model_stat_food.created_time = get_current_date()

            tmp_model_stat_food.total_count = item[1]
            tmp_model_stat_food.total_pay_money = item[2]
            tmp_model_stat_food.updated_time = get_current_date()

            # 模拟数据
            if tmp_model_stat_food.total_count == 0:
                tmp_model_stat_food.total_count = random.randint(50, 100)
            if tmp_model_stat_food.total_pay_money == 0:
                tmp_model_stat_food.total_pay_money = random.randint(1000, 1010)

            with db.auto_commit():
                db.session.add(tmp_model_stat_food)

        return

    # site统计
    def stat_site(self, params):
        act = params['act']
        date = params['date']
        date_from = params['date_from']
        date_to = params['date_to']
        app.logger.info("act:{0},from:{1},to:{2}".format(act, date_from, date_to))

        stat_pay = db.session.query(
            func.sum(PayOrder.total_price).label("total_pay_money")) \
            .filter(PayOrder.status == 1) \
            .filter(PayOrder.created_time >= date_from,
                    PayOrder.created_time <= date_to).first()

        stat_member_count = Member.query.count()
        stat_new_member_count = Member.query.filter(
            Member.created_time >= date_from,
            Member.created_time <= date_to).count()

        stat_order_count = PayOrder.query.filter_by(status=1)\
            .filter(PayOrder.created_time >= date_from, PayOrder.created_time <= date_to)\
            .count()

        stat_share_count = WxShareHistory.query.filter(
            WxShareHistory.created_time >= date_from,
            WxShareHistory.created_time <= date_to).count()

        tmp_stat_site = StatDailySite.query.filter_by(date=date).first()
        if tmp_stat_site:
            tmp_model_stat_site = tmp_stat_site
        else:
            tmp_model_stat_site = StatDailySite()
            tmp_model_stat_site.date = date
            tmp_model_stat_site.created_time = get_current_date()

        tmp_model_stat_site.total_pay_money = stat_pay[0] if stat_pay[0] else 0.00
        tmp_model_stat_site.total_new_member_count = stat_new_member_count
        tmp_model_stat_site.total_member_count = stat_member_count
        tmp_model_stat_site.total_order_count = stat_order_count
        tmp_model_stat_site.total_shared_count = stat_share_count
        tmp_model_stat_site.updated_time = get_current_date()

        # 模拟数据
        if tmp_model_stat_site.total_pay_money == 0:
            tmp_model_stat_site.total_pay_money = random.randint(1000, 1010)
        tmp_model_stat_site.total_new_member_count = random.randint(50, 100)
        if tmp_model_stat_site.total_new_member_count == 0:
            tmp_model_stat_site.total_member_count += \
                tmp_model_stat_site.total_new_member_count
        if tmp_model_stat_site.total_order_count == 0:
            tmp_model_stat_site.total_order_count = random.randint(900, 1000)
        if tmp_model_stat_site.total_shared_count == 0:
            tmp_model_stat_site.total_shared_count = random.randint(1000, 2000)

        with db.auto_commit():
            db.session.add(tmp_model_stat_site)

    # 模拟创建数据
    def test(self):
        import datetime
        now = datetime.datetime.now()
        for i in reversed(range(1, 30)):
            date_before = now + datetime.timedelta(days=-i)
            date = get_format_date(date=date_before, format="%Y-%m-%d")
            tmp_params = {
                'act': 'test',
                'date': date,
                'date_from': date + " 00:00:00",
                'date_to':  date + " 23:59:59"
            }
            self.test_food(date)
            self.stat_food(tmp_params)
            self.stat_member(tmp_params)
            self.stat_site(tmp_params)

    def test_food(self,date):
        from app.models.food.food import Food
        list = Food.query.all()
        if list:
            for item in list:
                model = FoodSaleChangeLog()
                model.food_id = item.id
                model.quantity = random.randint(1, 10)
                model.price = model.quantity * item.price
                model.member_id = 1
                model.created_time = date + " " + get_format_date(format="%H:%M:%S")
                with db.auto_commit():
                    db.session.add(model)
