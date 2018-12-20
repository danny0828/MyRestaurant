"""
 Created by Danny on 2018/11/29
"""
import hashlib, base64, random, string
__author__ = 'Danny'


class UserService:
    @staticmethod
    def gene_auth_code(user_info=None):
        m = hashlib.md5()
        s = "%s-%s-%s-%s" % (user_info.uid, user_info.login_name, user_info.login_pwd, user_info.login_salt)
        m.update(s.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def gene_pwd(pwd, salt):
        m = hashlib.md5()                     # 字符串转字节码
        s = "%s-%s" % (base64.encodebytes(pwd.encode("utf-8")), salt)
        m.update(s.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def gene_salt(length=16):
        key_list = [random.choice((string.ascii_letters + string.digits)) for i in range( length)]
        return ("".join(key_list))

