"""
 Created by Danny on 2018/12/16
"""
from app.models.queue_list import QueueList
from app.models.member.member_auth_bind import MemberAuthBind
from app.models.pay.pay_order import PayOrder
from app.models.pay.pay_order_item import PayOrderItem
from app.models.food.food import Food
from app.models.food.food_sale_change_log import FoodSaleChangeLog
from app.libs.helper import get_current_date
from app.models.base import db
import json, datetime, requests
from app.libs.pay.wechat_service import WeChatService
from app.app import app
from sqlalchemy import func
__author__ = 'Danny'


# python manager.py runjob -m queue/index
class JobTask:
    def __init__(self):
        pass

    def run(self, params):
        list = QueueList.query.filter_by(status=-1)\
            .order_by(QueueList.id.asc()).limit(1).all()
        for item in list:
            if item.queue_name == "pay":
                self.handle_pay(item)

            item.status = 1
            item.updated_time = get_current_date()
            with db.auto_commit():
                item

    def handle_pay(self, item):
        data = json.loads(item.data)
        if 'member_id' not in data or 'pay_order_id' not in data:
            return False

        member_auth_bind = MemberAuthBind.query.filter_by(member_id=data['member_id']).first()
        if not member_auth_bind:
            return False

        pay_order_info = PayOrder.query.filter_by(id=data['pay_order_id']).first()
        if not pay_order_info:
            return False

        #更新销售总量
        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
        notice_content = []
        if pay_order_items:
            date_from = datetime.datetime.now().strftime("%Y-%m-01 00:00:00")
            date_to = datetime.datetime.now().strftime("%Y-%m-31 23:59:59")
            for item in pay_order_items:
                tmp_food_info = Food.query.filter_by(id=item.food_id).first()
                if not tmp_food_info:
                    continue

                notice_content.append("%s %s份" % (tmp_food_info.name, item.quantity))

                tmp_stat_info = db.session.query(FoodSaleChangeLog,
                                                 func.sum(FoodSaleChangeLog.quantity).label("total")) \
                    .filter(FoodSaleChangeLog.food_id == item.food_id)\
                    .filter(FoodSaleChangeLog.created_time >= date_from,
                            FoodSaleChangeLog.created_time <= date_to).first()
                tmp_month_count = tmp_stat_info[1] if tmp_stat_info[1] else 0
                tmp_food_info.total_count += 1
                tmp_food_info.month_count = tmp_month_count
                with db.auto_commit():
                    tmp_food_info

        keyword1_val = "、".join(notice_content)
        keyword2_val = pay_order_info.note if pay_order_info.note else '无'
        keyword3_val = str(pay_order_info.total_price)
        keyword4_val = str(pay_order_info.order_number)
        keyword5_val = ""

        # 发送模板消息
        # https://developers.weixin.qq.com/miniprogram/dev/api/sendTemplateMessage.html
        target_wechat = WeChatService()
        access_token = target_wechat.get_access_token()
        headers = {'Content-Type': 'application/json'}
        url = "https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token=%s" % access_token
        params = {
            "touser": member_auth_bind.openid,
            "template_id": app.config['TEMPLATE_PAY_OK']['id'],
            "page": app.config['TEMPLATE_PAY_OK']['page'],
            "form_id": pay_order_info.prepay_id,
            "data": {
                "keyword1": {
                    "value": keyword1_val
                },
                "keyword2": {
                    "value": keyword2_val
                },
                "keyword3": {
                    "value": keyword3_val
                },
                "keyword4": {
                    "value": keyword4_val
                },
                "keyword5": {
                    "value": keyword5_val
                }
            }
        }

        r = requests.post(url=url, data=json.dumps(params).encode('utf-8'), headers=headers)
        r.encoding = "utf-8"
        app.logger.info(r.text)
        return True

