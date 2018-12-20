"""
 Created by Danny on 2018/11/28
"""
from app.web import static_bp
from flask import send_from_directory, current_app
__author__ = 'Danny'


@static_bp.route("/<path:filename>")
def index(filename):
    return send_from_directory(current_app.root_path + "/app/web/static/", filename)









