"""
 Created by Danny on 2018/12/3
"""
from flask import Blueprint
from app.web.api.v1 import member, food, cart, order, my
__author__ = 'Danny'


def create_blueprint_v1():
    v1_bp = Blueprint('v1', __name__)

    member.api.register(v1_bp)
    food.api.register(v1_bp)
    cart.api.register(v1_bp)
    order.api.register(v1_bp)
    my.api.register(v1_bp)
    return v1_bp










