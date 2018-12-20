"""
 Created by Danny on 2018/12/11
"""
from app.models.base import db, Base
from app.libs.helper import get_current_date
__author__ = 'Danny'


class MemberCart(Base):
    __tablename__ = 'member_cart'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.BigInteger, nullable=False, index=True, server_default=db.FetchedValue())
    food_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    quantity = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    @staticmethod
    def set_items(member_id=0, food_id=0, number=0):
        if member_id < 1 or food_id < 1 or number < 1:
            return False
        cart_info = MemberCart.query.filter_by(food_id=food_id, member_id=member_id).first()
        if cart_info:
            model_cart = cart_info
        else:
            model_cart = MemberCart()
            model_cart.member_id = member_id
            model_cart.created_time = get_current_date()

        model_cart.food_id = food_id
        model_cart.quantity = number
        model_cart.updated_time = get_current_date()
        with db.auto_commit():
            db.session.add(model_cart)
        return True

    @staticmethod
    def delete_item(member_id=0, items=None):
        if member_id < 1 or not items:
            return False
        with db.auto_commit():
            for item in items:
                MemberCart.query.filter_by(food_id=item['id'],
                                           member_id=member_id).delete()
        return True

