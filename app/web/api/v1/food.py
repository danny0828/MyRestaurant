"""
 Created by Danny on 2018/12/7
"""
from app.libs.redprint import Redprint
from app.models.food.food_category import FoodCategory
from app.models.food.food import Food
from app.libs.url_manager import UrlManager
from flask import jsonify, request, g
from sqlalchemy import or_
from app.libs.error_code import NotFound
from app.models.member.member_cart import MemberCart
from app.models.member.member_comments import MemberComments
from app.models.member.member import Member
from app.libs.token_auth import auth
from app.validators.forms import IdForm
from app.libs.helper import get_dict_filter_field, select_filter_obj
__author__ = 'Danny'

api = Redprint('food')


@api.route('/index')
def food_index():
    resp = {}
    c_list = FoodCategory.query.filter_by(status=1).order_by(FoodCategory.weight.desc()).all()
    data_c_list = []
    data_c_list.append({
        'id': 0,
        'name': '全部'
    })
    if c_list:
        for item in c_list:
            temp_data = {
                'id': item.id,
                'name': item.name
            }
            data_c_list.append(temp_data)
    resp['category_list'] = data_c_list

    food_list = Food.query.filter_by(status=1).order_by(
        Food.total_count.desc(), Food.id.desc()).limit(3).all()
    data_food_list = []
    if food_list:
        for item in food_list:
            temp_data = {
                'id': item.id,
                'pic_url': UrlManager.build_image_url(item.main_image)
            }
            data_food_list.append(temp_data)
    resp['food_list'] = data_food_list
    return jsonify(resp)


@api.route('/search')
def food_search():
    resp = {}
    req = request.values
    category_id = int(req['category_id']) if 'category_id' in req else 0
    search_key = str(req['search_key']) if 'search_key' in req else ''
    p = int(req['p']) if 'p' in req else 1

    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size

    query = Food.query.filter_by(status=1)
    if category_id > 0:
        query = query.filter_by(cat_id=category_id)

    if search_key:
        query = query.filter(or_(Food.name.ilike(
            "%{0}%".format(search_key)),
            Food.tags.ilike("%{0}%".format(search_key))))

    food_list = query.order_by(Food.total_count.desc(), Food.id.desc())\
        .offset(offset).limit(page_size).all()
    data_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': "%s"%(item.name),
                'price': str(item.price),
                'min_price': str(item.price),
                'pic_url': UrlManager.build_image_url(item.main_image)
            }
            data_food_list.append(tmp_data)
    resp['foods'] = data_food_list
    resp['has_more'] = 0 if len(data_food_list) < page_size else 1
    return jsonify(resp)


@api.route('/info', methods=["POST"])
@auth.login_required
def food_info():
    form = IdForm().validate_for_api()
    id = form.id.data
    # req = request.values
    # id = int(req['id']) if 'id' in req else 0
    food_info = Food.query.filter_by(id=id).first()
    if not food_info or not food_info.status:
        return NotFound(msg='美食已下架')
    member_info = g.user
    cart_number = 0
    if member_info:
        cart_number = MemberCart.query.filter_by(member_id=member_info.uid).count()
    resp = {}
    resp['info'] = {
        "id": food_info.id,
        "name": food_info.name,
        "summary": food_info.summary,
        "total_count": food_info.total_count,
        "comment_count": food_info.comment_count,
        'main_image': UrlManager.build_image_url(food_info.main_image),
        "price": str(food_info.price),
        "stock": food_info.stock,
        "pics": [UrlManager.build_image_url(food_info.main_image)]
    }
    resp['cart_number'] = cart_number
    return jsonify(resp)


@api.route("/comments", methods=["POST"])
@auth.login_required
def food_comments():
    form = IdForm().validate_for_api()
    id = form.id.data
    query = MemberComments.query.filter(MemberComments.food_ids.ilike("%_{0}_%".format(id)))
    list = query.order_by(MemberComments.id.desc()).limit(5).all()
    data_list = []
    if list:
        member_map = get_dict_filter_field(Member, Member.id, "id",
                                           select_filter_obj(list, "member_id"))
        for item in list:
            if item.member_id not in member_map:
                continue
            tmp_member_info = member_map[ item.member_id ]
            tmp_data = {
                'score': item.score_desc,
                'date': item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "content": item.content,
                "user": {
                    'nickname': tmp_member_info.nickname,
                    'avatar_url': tmp_member_info.avatar,
                }
            }
            data_list.append(tmp_data)
    resp = {}
    resp['list'] = data_list
    resp['count'] = query.count()
    return jsonify(resp)







