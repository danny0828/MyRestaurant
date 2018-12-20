"""
 Created by Danny on 2018/12/13
"""
import hashlib, requests, uuid, json, datetime
import xml.etree.ElementTree as E_Tree
from app.libs.error_code import ParameterException
from flask import current_app
from app.models.pay.auth_access_token import AuthAccessToken
from app.models.base import db
from app.libs.helper import get_current_date
__author__ = 'Danny'


class WeChatService:
    def __init__(self, merchant_key=None):
        # https://pay.weixin.qq.com/   API密钥
        self.merchant_key = merchant_key

    """
    生成签名
    https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=4_3
    stringA="appid=wxd930ea5d5a258f4f&body=test&device_info=1000&mch_id=10000100&nonce_str=ibuaiVcKdpRxkhJA";
    
    stringSignTemp=stringA+"&key=192006250b4c09247ec02edce69f6a2d" //注：key为商户平台设置的密钥key

    sign=MD5(stringSignTemp).toUpperCase()="9A0A8659F005D6984697E2CA0A9CF3B7" //注：MD5签名方式

    sign=hash_hmac("sha256",stringSignTemp,key).toUpperCase()="6A9AE1657590FD6257D693A078E1C3E4BB6BA4DC30B23E0EE2496E54170DACD6" //注：HMAC-SHA256签名方式    
    """
    def create_sign(self, pay_data):
        stringA = '&'.join(
            ["{0}={1}".format(k, pay_data.get(k)) for k in sorted(pay_data)])
        stringSignTemp = '{0}&key={1}'.format(stringA, self.merchant_key)
        sign = hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest()
        return sign.upper()

    """
    获取支付信息
    https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=9_1
    """
    def get_pay_info(self, pay_data=None):
        sign = self.create_sign(pay_data)
        pay_data['sign'] = sign
        xml_data = self.dict_to_xml(pay_data)
        headers = {'Content-Type': 'application/xml'}
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        r = requests.post(url=url, data=xml_data.encode('utf-8'), headers=headers)
        r.encoding = "utf-8"
        print(r.text)
        if r.status_code == 200:
            prepay_id = self.xml_to_dict(r.text).get('prepay_id')
            if not prepay_id:
                raise ParameterException(msg='无法获取支付信息')
            # https://developers.weixin.qq.com/miniprogram/dev/api/wx.requestPayment.html
            pay_sign_data = {
                'appId': pay_data.get('appid'),
                'timeStamp': pay_data.get('out_trade_no'),
                'nonceStr': pay_data.get('nonce_str'),
                'package': 'prepay_id={0}'.format(prepay_id),
                'signType': 'MD5'
            }
            pay_sign = self.create_sign(pay_sign_data)
            pay_sign_data.pop('appId')
            pay_sign_data['paySign'] = pay_sign
            pay_sign_data['prepay_id'] = prepay_id
            return pay_sign_data

        return False

    def dict_to_xml(self, dict_data):
        xml = ["<xml>"]
        for k, v in dict_data.items():
            xml.append("<{0}>{1}</{0}>".format(k, v))
        xml.append("</xml>")
        return "".join(xml)

    def xml_to_dict(self,xml_data):
        xml_dict = {}
        root = E_Tree.fromstring(xml_data)
        for child in root:
            xml_dict[child.tag] = child.text
        return xml_dict

    # 获取随机字符串
    def get_nonce_str(self):
        return str(uuid.uuid4()).replace('-', '')

    # https://developers.weixin.qq.com/miniprogram/dev/api/getAccessToken.html
    def get_access_token(self):
        token = None

        token_info = AuthAccessToken.query.filter(AuthAccessToken.expired_time >= get_current_date()).first()
        if token_info:
            token = token_info.access_token
            return token

        config_mina = current_app.config['MINA_APP']
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}"\
            .format(config_mina['appid'],config_mina['appkey'])

        r = requests.get(url=url)
        if r.status_code != 200 or not r.text:
            return token

        data = json.loads(r.text)
        now = datetime.datetime.now()
        date = now + datetime.timedelta(seconds=data['expires_in'] - 200)
        model_token = AuthAccessToken()
        model_token.access_token = data['access_token']
        model_token.expired_time = date.strftime("%Y-%m-%d %H:%M:%S")
        model_token.created_time = get_current_date()
        with db.auto_commit():
            db.session.add(model_token)

        return data['access_token']






