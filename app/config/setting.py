"""
 Created by Danny on 2018/11/28
"""
__author__ = 'Danny'

SERVER_PORT = 6606
RELEASE_VERSION = '201811280916'

JSON_AS_ASCII = False  # 网页返回json显示中文
AUTH_COOKIE_NAME = 'd_food'

# 不检查的url
IGNORE_URLS = [
    '^/user/login'
]

IGNORE_CHECK_LOGIN_URLS = [
    '^/static',
    '^/favicon.ico'
]

API_IGNORE_URLS = [
    "^/api"
]

PAGE_SIZE = 50
PAGE_DISPLAY = 10

STATUS_MAPPING = {
    '1': '正常',
    '0': '已删除'
}

TOKEN_EXPIRATION = 30 * 24 * 3600  # TOKEN有效期

UPLOAD = {
    'ext': ['jpg', 'gif', 'bmp', 'jpeg', 'png'],
    'prefix_path': '/app/web/static/upload/',
    'prefix_url': '/static/upload/'
}

APP = {
    'domain': 'http://localhost:6606'
}

PAY_STATUS_MAPPING = {
    "1": "已支付",
    "-8": "待支付",
    "0": "已关闭"
}

PAY_STATUS_DISPLAY_MAPPING = {
    0: "订单关闭",
    1: "支付成功",
    -8: "待支付",
    -7: "待发货",
    -6: "待确认",
    -5: "待评价"
}








