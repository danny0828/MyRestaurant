"""
 Created by Danny on 2018/12/3
"""
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, length, NumberRange, Regexp
from app.validators.base import BaseForm as Form
from app.libs.enums import ClientTypeEnum, OrderStatusEnum
__author__ = 'Danny'


class ClientForm(Form):
    account = StringField(validators=[DataRequired(message='不允许为空'), length(  # code
        min=5, max=32
    )])
    secret = StringField()
    type = IntegerField(validators=[DataRequired()])

    def validate_type(self, value):
        try:
            client = ClientTypeEnum(value.data)
            self.type.data = client
        except ValueError as e:
            raise e


class ShareForm(Form):
    url = StringField(validators=[DataRequired()])


class IdForm(Form):
    # 'POST'时，可以发送int 'GET'时，测试参数都是''，所以如果要验证数值，要用post传递参数
    id = IntegerField(validators=[DataRequired(), NumberRange(min=1, message='最小值为1')])


class CartForm(IdForm):
    number = IntegerField(validators=[DataRequired(), NumberRange(min=1, message='最小值为1')])


class MyOrderForm(Form):
    status = IntegerField(validators=[NumberRange(min=-8, max=1)])

    def validate_status(self, value):
        try:
            client = OrderStatusEnum(value.data)
            self.status.data = client
        except ValueError as e:
            raise e


class PayForm(Form):
    order_sn = StringField(validators=[DataRequired(), length(min=32, max=32)])


class OrderCreateForm(Form):
    type = StringField(validators=[DataRequired()])
    goods = StringField(validators=[DataRequired()])
    express_address_id = IntegerField(validators=[DataRequired()])
    note = StringField()


class OrderOpsForm(PayForm):
    act = StringField(validators=[DataRequired()])


class CommentForm(PayForm):
    content = StringField(validators=[DataRequired()])
    score = IntegerField(validators=[DataRequired()])


class AddressForm(Form):
    id = IntegerField(validators=[NumberRange(min=0)])
    nickname = StringField(validators=[DataRequired(), length(min=2, max=10, message='请填写正确的联系人姓名')])
    mobile = \
        StringField(validators=[DataRequired(),
                                Regexp('^1[0-9]{10}$', 0, '请输入正确的手机号')])
    province_id = IntegerField(validators=[NumberRange(min=0)])
    province_str = StringField(validators=[DataRequired('请选择地区'), length(min=2, max=30)])
    city_id = IntegerField(validators=[NumberRange(min=0)])
    city_str = StringField(validators=[DataRequired(), length(min=2, max=30)])
    district_id = IntegerField()
    district_str = StringField()
    address = StringField(validators=[DataRequired('请填写详细地址'), length(min=5, max=50)])


class OpsForm(IdForm):
    act = StringField(validators=[DataRequired()])






