"""
 Created by Danny on 2018/12/5
"""
from flask import current_app
from werkzeug.utils import secure_filename
from app.libs.helper import get_current_date
import os, stat, uuid
from app.models.images import Image
from app.models.base import db
__author__ = 'Danny'


class UploadService:
    @staticmethod
    def upload_by_file(file):
        config_upload = current_app.config['UPLOAD']
        resp = {'code': 200, 'msg': '操作成功', 'data': {}}
        file_name = secure_filename(file.filename)
        ext = file_name.rsplit('.', 1)[1]
        if ext not in config_upload['ext']:
            resp['code'] = -1
            resp['msg'] = "不允许的扩展类型文件"
            return resp

        root_path = current_app.root_path + config_upload['prefix_path']
        file_dir = get_current_date('%Y%m%d')
        save_dir = root_path + file_dir
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
            os.chmod(save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)  # 给文件夹授权

        file_name = str(uuid.uuid4()).replace('-', '') + '.' + ext  # 根据硬件和时间创建一个唯一不重复的字符串
        file.save('{0}/{1}'.format(save_dir, file_name))

        model_image = Image()
        model_image.file_key = file_dir + '/' + file_name
        model_image.created_time = get_current_date()
        with db.auto_commit():
            db.session.add(model_image)

        resp['data'] = {
            'file_key': file_dir + "/" + file_name
        }
        return resp









