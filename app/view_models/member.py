"""
 Created by Danny on 2018/12/4
"""
from flask import current_app
__author__ = 'Danny'


class MemberViewModel:
    def __init__(self, member):
        self.id = member.id
        self.avatar = member.avatar
        self.nickname = member.nickname
        self.sex = member.sex
        self.status = member.status

    @property
    def status_desc(self):
        return current_app.config['STATUS_MAPPING'][str(self.status)]

    @property
    def sex_desc(self):
        sex_mapping = {
            0: '未知',
            1: '男',
            2: '女'
        }
        return sex_mapping[self.sex]


class MembersViewModel:
    def __init__(self, member_list):
        self.members = []
        self.__member_list = member_list
        self.members = self.__parse()

    def __parse(self):
        temp_members = []
        for member in self.__member_list:
            my_member = MemberViewModel(member)
            temp_members.append(my_member)
        return temp_members









