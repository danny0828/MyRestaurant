"""
 Created by Danny on 2018/11/28
"""
__author__ = 'Danny'


SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://danny:123456@localhost:3306/food'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = False  # 打印所有sql语句

SECRET_KEY = '\xc5\xb6\xc8\xb6\xf6]\xebE\x16\xb6\x1c\x82zML\x80\xf6\xac\x88 \xae\x01\xe67\xbc'

MINA_APP = {
    'appid': 'wx06416435434094ee',
    'appkey': 'cec0d21bfeeb22984e9b9ee639518709',
    'merchant_key': 'xxxxxx',  # 商户平台设置的密钥key
    'mch_id': '1443337302',    # 商户号
    'callback_url': '/v1/order/callback'
}

TEMPLATE_PAY_OK = {
    'id': 'G2qvvmv-D2ZveYMKk2xIcDh5DWI6GVBBTWtnHrqzryQ',
    'page': 'pages/my/order_list'
}









