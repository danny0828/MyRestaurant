"""
 Created by Danny on 2018/11/28
"""
import time
from flask import current_app
__author__ = 'Danny'


class UrlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def build_url(path):
        return path

    @staticmethod
    def build_static_url(path):
        # 通过更新版本号，使js文件可以实时刷新(不用通过ctrl+F5)
        release_version = current_app.config.get('RELEASE_VERSION')
        ver = release_version if release_version else "%s" % (int(time.time()))
        path = "/static" + path + "?ver=" + ver
        return UrlManager.build_url(path)

    @staticmethod
    def build_image_url(path):
        app_config = current_app.config['APP']
        url = app_config['domain'] + current_app.config['UPLOAD']['prefix_url'] + path
        return url
