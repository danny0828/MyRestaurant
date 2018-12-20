"""
 Created by Danny on 2018/12/3
"""
import requests, json
from flask import current_app
import random, string, hashlib
__author__ = 'Danny'


class MemberService:
    @staticmethod
    def gene_auth_code(member_info=None):
        m = hashlib.md5()
        s = "%s-%s-%s" % (member_info.id, member_info.salt, member_info.status)
        m.update(s.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def gene_salt(length=16):
        key_list = [random.choice((string.ascii_letters + string.digits)) for i in range(length)]
        return ("".join(key_list))

    @staticmethod
    def get_wechat_openid(code):
        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code" \
            .format(current_app.config['MINA_APP']['appid'],
                    current_app.config['MINA_APP']['appkey'], code)
        r = requests.get(url)
        res = json.loads(r.text)  # 把字符串变成json格式，方便用res['openid']获取
        openid = None
        if 'openid' in res:
            openid = res['openid']
        return openid










