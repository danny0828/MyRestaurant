"""
 Created by Danny on 2018/12/5
"""
from app.web import upload_bp
from flask import request, current_app, jsonify
import json, re
from app.libs.upload_service import UploadService
from app.libs.url_manager import UrlManager
from app.models.images import Image
__author__ = 'Danny'


@upload_bp.route('/ueditor', methods=['GET', 'POST'])
def ueditor():
    req = request.values
    action = req['action'] if 'action' in req else ''

    if action == 'config':  # ueditor控件获取参数
        root_path = current_app.root_path
        # root_path = root_path.replace("\\", '/')
        config_path = "{0}/app/web/static/plugins/ueditor/upload_config.json".format(
            root_path)
        # config_path = config_path.replace("\\", '/')
        with open(config_path, encoding="utf-8") as fp:
            try:
                config_data = json.loads(re.sub(r'\/\*.*\*/', '', fp.read()))
            except:
                config_data = {}
        return jsonify(config_data)

    if action == 'uploadimage':  # 上传图片时调用
        return upload_image()

    if action == 'listimage':    # 在线管理时调用
        return list_image()


    return 'u u u u u u'


def upload_image():
    resp = {'state': 'SUCCESS', 'url': '', 'title': '', 'original': ''}
    file_target = request.files
    upfile = file_target['upfile'] if 'upfile' in file_target else None
    if upfile is None:
        resp['state'] = '上传失败'
        return jsonify(resp)

    ret = UploadService.upload_by_file(upfile)
    if ret['code'] != 200:
        resp['state'] = '上传失败:' + ret['msg']
        return jsonify(resp)

    resp['url'] = UrlManager.build_image_url(ret['data']['file_key'])
    return jsonify(resp)


def list_image():
    resp = {'state': 'SUCCESS', 'list': [], 'start': 0, 'total': 0}

    req = request.values

    start = int(req['start']) if 'start' in req else 0
    page_size = int(req['size']) if 'size' in req else 20

    query = Image.query
    if start > 0:                                       # 倒叙才这样处理
        query = query.filter(Image.id < start)

    # i_list = query.order_by(
    #      Image.id).offset(start).limit(page_size).all()   # 正序用偏移量比较方便 数量
    i_list = query.order_by(Image.id.desc()).limit(page_size).all()
    images = []
    if i_list:
        for item in i_list:
            images.append({'url': UrlManager.build_image_url(item.file_key)})
            start = item.id

    resp['list'] = images
    resp['start'] = start
    resp['total'] = len(images)

    return jsonify(resp)


@upload_bp.route("/pic", methods=["GET", "POST"])
def upload_pic():
    file_target = request.files
    up_file = file_target['pic'] if 'pic' in file_target else None
    callback_target = 'window.parent.upload'
    if up_file is None:
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败")  # 调用set.js里的upload.error

    ret = UploadService.upload_by_file(up_file)
    if ret['code'] != 200:
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败：" + ret['msg'])

    return "<script type='text/javascript'>{0}.success('{1}')</script>".format(callback_target, ret['data']['file_key'])






