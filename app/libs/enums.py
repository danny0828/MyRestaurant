"""
 Created by Danny on 2018/12/3
"""
from enum import Enum
__author__ = 'Danny'


class ClientTypeEnum(Enum):
    USER_EMAIL = 100
    USER_MOBILE = 101

    # 微信小程序
    USER_MINA = 200
    # 微信公众号
    USER_WX = 201


class OrderStatusEnum(Enum):
    WAIT = -8
    SEND = -7
    CONFIRM = -6
    SAY = -5
    OK = 1
    CLOSE = 0









