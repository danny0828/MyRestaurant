"""
 Created by Danny on 2018/11/28
"""
from flask import Flask as _Flask
from flask_script import Manager
from app.models.base import db
import os
from flask_login import LoginManager
from flask.json import JSONEncoder as _JSONEncoder
from datetime import date

from app.libs.error_code import ServerError
__author__ = 'Danny'


# class App(Flask):
#     def __init__(self, import_name):
#         super(App, self).__init__(import_name)

login_manager = LoginManager()


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        raise ServerError()


class Flask(_Flask):
    json_encoder = JSONEncoder


def create_app(template_folder=None, root_path=None):
    app = Flask(__name__, template_folder=template_folder, root_path=root_path, static_folder=None)
    if "ops_config" in os.environ:
        app.config.from_pyfile('config/%s_setting.py' % os.environ['ops_config'])
    else:
        app.config.from_object('app.config.secure')
        app.config.from_object('app.config.setting')

    # register_blueprint(app)

    login_manager.init_app(app)
    login_manager.login_view = 'user_page.login'
    login_manager.login_message = '请先登录或注册'

    # mail.init_app(app)

    db.init_app(app)
    # db.create_all(app=app)

    # 函数模板: 是模板可以调用python函数
    from app.libs.url_manager import UrlManager
    app.add_template_global(UrlManager.build_static_url, 'buildStaticUrl')
    app.add_template_global(UrlManager.build_url, 'buildUrl')
    app.add_template_global(UrlManager.build_image_url, 'buildImageUrl')
    return app


def register_blueprint(app):
    from app.web import web, user_bp, static_bp, \
        account_bp, food_bp, member_bp, finance_bp, stat_bp, upload_bp, chart_bp
    from app.web.api.v1 import create_blueprint_v1
    app.register_blueprint(web, url_prefix='/')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(static_bp, url_prefix='/static')
    app.register_blueprint(account_bp, url_prefix="/account")
    app.register_blueprint(food_bp, url_prefix="/food")
    app.register_blueprint(member_bp, url_prefix="/member")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(stat_bp, url_prefix="/stat")
    app.register_blueprint(create_blueprint_v1(), url_prefix="/v1")
    app.register_blueprint(upload_bp, url_prefix="/upload")
    app.register_blueprint(chart_bp, url_prefix="/chart")


app = create_app(template_folder=os.getcwd() + "/app/web/templates/", root_path=os.getcwd())
register_blueprint(app)  # 把注册蓝图放到这里可以解决登录拦截器无法import app的问题
manager = Manager(app)









