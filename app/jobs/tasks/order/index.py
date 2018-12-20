"""
 Created by Danny on 2018/12/17
"""
import datetime
from app.models.pay.pay_order import PayOrder
from app.libs.helper import get_format_date
from app.libs.pay.pay_service import PayService
from app.app import app
__author__ = 'Danny'


# python manager.py runjob -m order/index
class JobTask:
    def __init__(self):
        pass

    def run(self, params):
        now = datetime.datetime.now()
        date_before_30min = now + datetime.timedelta(minutes=-30)
        list = PayOrder.query.filter_by(status=-8).\
            filter(PayOrder.created_time <= get_format_date(date=date_before_30min)).all()
        if not list:
            app.logger.info("no data~~")
            return

        pay_target = PayService()
        for item in list:
            pay_target.close_order(pay_order_id=item.id)
        app.logger.info("it's over~~")









