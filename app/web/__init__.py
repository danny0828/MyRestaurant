"""
 Created by Danny on 2018/11/28
"""
from flask import Blueprint
__author__ = 'Danny'

web = Blueprint('web', __name__)  # template_folder='templates'
user_bp = Blueprint('user_page', __name__)
static_bp = Blueprint('static', __name__)
account_bp = Blueprint('account_page', __name__)
food_bp = Blueprint('food_page', __name__)
finance_bp = Blueprint('finance_page', __name__)
member_bp = Blueprint('member_page', __name__)
stat_bp = Blueprint('stat_page', __name__)
upload_bp = Blueprint('upload_page', __name__)
chart_bp = Blueprint('chart_page', __name__)


# from app.web.interceptors.auth_interceptor import *     使用flask-login代替
# from app.web.interceptors.ApiAuthInterceptor import *   使用HTTPBasicAuth代替
from app.web.interceptors.error_interceptor import *

from app.web.controllers import index
from app.web.controllers import user
from app.web.controllers import static
from app.web.controllers import stat
from app.web.controllers import account
from app.web.controllers import member
from app.web.controllers import finance
from app.web.controllers import food
from app.web.controllers import upload
from app.web.controllers import chart











