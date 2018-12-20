"""
 Created by Danny on 2018/11/28
"""
from flask import render_template, request, current_app, redirect
from app.web import food_bp
from app.models.food.food_category import FoodCategory
from app.models.food.food import Food
from app.models.food.food_stock_change_log import FoodStockChangeLog
from app.libs.error_code import AjaxSuccess, AjaxFail
from app.libs.helper import get_current_date, i_pagination, get_dict_filter_field
from app.models.base import db
from decimal import Decimal
from app.libs.url_manager import UrlManager
from sqlalchemy import or_
from app.libs.pay.pay_service import PayService
from flask_login import login_required
__author__ = 'Danny'


@food_bp.route("/index")
@login_required
def index():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = Food.query
    if 'mix_kw' in req:
        rule = or_(Food.name.ilike("%{0}%".format(req['mix_kw'])), Food.tags.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter(rule)

    if 'status' in req and int(req['status'] ) > -1:
        query = query.filter(Food.status == int(req['status']))

    if 'cat_id' in req and int(req['cat_id']) > 0:
        query = query.filter(Food.cat_id == int(req['cat_id']))

    page_params = {
        'total': query.count(),
        'page_size': current_app.config['PAGE_SIZE'],
        'page': page,
        'display': current_app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace('&p={}'.format(page), '')
    }

    pages = i_pagination(page_params)
    offset = (page - 1) * current_app.config['PAGE_SIZE']
    f_list = query.order_by(Food.id.desc()).offset(offset).limit(current_app.config['PAGE_SIZE'] ).all()

    cat_mapping = get_dict_filter_field(FoodCategory, FoodCategory.id, 'id', [])
    resp_data['list'] = f_list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['status_mapping'] = current_app.config['STATUS_MAPPING']
    resp_data['cat_mapping'] = cat_mapping
    resp_data['current'] = 'index'
    return render_template("food/index.html", **resp_data)


@food_bp.route("/info")
@login_required
def info():
    resp_data = {}
    req = request.args
    f_id = int(req.get("id", 0))
    back_url = UrlManager.build_url("/food/index")

    if f_id < 1:
        return redirect(back_url)

    f_info = Food.query.filter_by(id=f_id).first()
    if not info:
        return redirect(back_url)

    stock_change_list = FoodStockChangeLog.query.filter(FoodStockChangeLog.food_id == f_id)\
        .order_by(FoodStockChangeLog.id.desc()).all()

    resp_data['info'] = f_info
    resp_data['stock_change_list'] = stock_change_list
    resp_data['current'] = 'index'
    return render_template("food/info.html", **resp_data)


@food_bp.route("/set", methods=['GET', 'POST'])
@login_required
def set():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        id = int(req.get('id', 0))
        info = Food.query.filter_by(id=id).first()
        if info and info.status != 1:
            return redirect(UrlManager.build_url('/food/index'))

        c_list = FoodCategory.query.all()
        resp_data['info'] = info
        resp_data['c_list'] = c_list
        resp_data['current'] = 'index'
        return render_template("food/set.html", **resp_data)

    req = request.values
    id = int(req['id']) if 'id' in req and req['id'] else 0
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    name = req['name'] if 'name' in req else ''
    price = req['price'] if 'price' in req else ''
    main_image = req['main_image'] if 'main_image' in req else ''
    summary = req['summary'] if 'summary' in req else ''
    stock = int(req['stock']) if 'stock' in req else ''
    tags = req['tags'] if 'tags' in req else ''

    if cat_id < 1:
        return AjaxFail('请选择分类')

    if name is None or len(name) < 1:
        return AjaxFail('请输入符合规范的名称')

    if not price or len(price) < 1:
        return AjaxFail('请输入符合规范的售卖价格')

    price = Decimal(price).quantize(Decimal('0.00'))
    if price <= 0:
        return AjaxFail('请输入符合规范的售卖价格')

    if main_image is None or len(main_image) < 3:
        return AjaxFail('请上传封面图')

    if summary is None or len(summary) < 3:
        return AjaxFail('请输入图书描述，并不能少于10个字符')

    if stock < 1:
        return AjaxFail('请输入符合规范的库存量')

    if tags is None or len(tags) < 1:
        return AjaxFail('请输入标签，便于搜索')

    food_info = Food.query.filter_by(id=id).first()
    before_stock = 0
    if food_info:
        model_food = food_info
        before_stock = model_food.stock
    else:
        model_food = Food()
        model_food.status = 1
        model_food.created_time = get_current_date()

    model_food.cat_id = cat_id
    model_food.name = name
    model_food.price = price
    model_food.main_image = main_image
    model_food.summary = summary
    model_food.stock = stock
    model_food.tags = tags
    model_food.updated_time = get_current_date()

    with db.auto_commit():
        db.session.add(model_food)

    PayService.set_stock_change_log(model_food.id, int(stock) - int(before_stock), "后台修改")

    return AjaxSuccess()


@food_bp.route("/category")
@login_required
def cat():
    resp_data = {}
    req = request.values
    query = FoodCategory.query

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(FoodCategory.status == int(req['status']))

    c_list = query.order_by(FoodCategory.weight.desc(), FoodCategory.id.desc()).all()
    resp_data['list'] = c_list
    resp_data['search_con'] = req
    resp_data['status_mapping'] = current_app.config['STATUS_MAPPING']
    resp_data['current'] = 'category'
    return render_template("food/category.html", **resp_data)


@food_bp.route("/category-set", methods=["GET", "POST"])
@login_required
def category_set():
    if request.method == "GET":
        resp_data = {}
        req = request.args
        c_id = int(req.get("id", 0))
        c_info = None
        if c_id:
            c_info = FoodCategory.query.filter_by(id=c_id).first()
        resp_data['info'] = c_info
        resp_data['current'] = 'category'
        return render_template("food/category_set.html", **resp_data)

    req = request.values

    c_id = req['id'] if 'id' in req else 0
    name = req['name'] if 'name' in req else ''
    weight = int(req['weight']) if ('weight' in req and int(req['weight']) > 0) else 1

    if name is None or len(name) < 1:
        return AjaxFail('请输入符合规范的分类名称')

    food_category_info = FoodCategory.query.filter_by(id=c_id).first()
    if food_category_info:
        model_food_category = food_category_info
    else:
        model_food_category = FoodCategory()
        model_food_category.created_time = get_current_date()
    model_food_category.name = name
    model_food_category.weight = weight
    model_food_category.updated_time = get_current_date()
    with db.auto_commit():
        db.session.add(model_food_category)
    return AjaxSuccess()


@food_bp.route("/category-ops", methods=["POST"])
@login_required
def category_ops():
    req = request.values

    c_id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not c_id:
        return AjaxFail('请选择要操作的账号')

    if act not in ['remove', 'recover']:
        return AjaxFail('操作有误，请重试')

    food_category_info = FoodCategory.query.filter_by(id=c_id).first()
    if not food_category_info:
        return AjaxFail('指定分类不存在')

    if act == "remove":
        food_category_info.status = 0
    elif act == "recover":
        food_category_info.status = 1

        food_category_info.update_time = get_current_date()
    with db.auto_commit():
        db.session.add(food_category_info)
    return AjaxSuccess()


@food_bp.route("/ops", methods=["POST"])
@login_required
def ops():
    req = request.values

    f_id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''

    if not f_id:
        return AjaxFail('请选择要操作的账号')

    if act not in ['remove', 'recover']:
        return AjaxFail('操作有误，请重试')

    food_info = Food.query.filter_by(id=f_id).first()
    if not food_info:
        return AjaxFail('指定美食不存在')

    if act == "remove":
        food_info.status = 0
    elif act == "recover":
        food_info.status = 1

    food_info.updated_time = get_current_date()
    with db.auto_commit():
        food_info
    return AjaxSuccess()









