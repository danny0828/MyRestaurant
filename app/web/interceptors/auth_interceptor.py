"""
 Created by Danny on 2018/11/29
"""
from flask import request, redirect, current_app, g
from app.models.user import User
from app.libs.user_service import UserService
from app.libs.url_manager import UrlManager
import re
from app.app import app
from app.libs.log_service import LogService
__author__ = 'Danny'

"""
登录拦截器:这种方式可以自己定义一个cookie变量名

flask_login是生成一个session

2种方式都可以
1、cookie数据存放在客户的浏览器上，session数据放在服务器上。
2、cookie不是很安全，别人可以分析存放在本地的COOKIE并进行COOKIE欺骗
   考虑到安全应当使用session。
3、session会在一定时间内保存在服务器上。当访问增多，会比较占用你服务器的性能
   考虑到减轻服务器性能方面，应当使用COOKIE。
4、单个cookie保存的数据不能超过4K，很多浏览器都限制一个站点最多保存20个cookie。
5、建议：
   将登陆信息等重要信息存放为SESSION
   其他信息如果需要保留，可以放在COOKIE中
"""

@app.before_request
def before_request():
    ignore_urls = current_app.config['IGNORE_URLS']
    ignore_check_login_urls = current_app.config['IGNORE_CHECK_LOGIN_URLS']
    path = request.path

    # 如果是静态文件就不要查询用户信息了
    pattern = re.compile('%s' % "|".join(ignore_check_login_urls))
    if pattern.match(path):
        return

    if '/v1' in path:
        return

    user_info = check_login()
    g.current_user = None
    if user_info:
        g.current_user = user_info

    #加入日志
    LogService.add_access_log()

    pattern = re.compile('%s' % "|".join(ignore_urls))
    if pattern.match(path):
        return

    if not user_info:
        return redirect(UrlManager.build_url("/user/login"))
    return


def check_login():
    cookies = request.cookies
    auth_cookie = cookies[current_app.config['AUTH_COOKIE_NAME']] if current_app.config['AUTH_COOKIE_NAME'] in cookies else None
    # current_app.logger.info(auth_cookie)

    if auth_cookie is None:
        return False

    auth_info = auth_cookie.split("#")
    if len(auth_info) != 2:
        return False

    try:
        user_info = User.query.filter_by(uid=auth_info[1]).first()
    except Exception:
        return False

    if user_info is None:
        return False

    if auth_info[0] != UserService.gene_auth_code(user_info):
        return False

    if user_info.status != 1:
        return False

    return user_info

