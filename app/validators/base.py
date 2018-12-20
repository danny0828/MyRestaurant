"""
 Created by Danny on 2018/12/3
"""
from wtforms.form import Form

from app.libs.error_code import ParameterException
from flask import request
__author__ = 'Danny'


class BaseForm(Form):
    def __init__(self):
        data = request.get_json(silent=True)
        args = request.args.to_dict()
        super(BaseForm, self).__init__(data=data, **args)

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()
        if not valid:
            raise ParameterException(msg=self.errors)
        return self








