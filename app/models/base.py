"""
 Created by Danny on 2018/11/28
"""
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from contextlib import contextmanager
from app.libs.error_code import NotFound
__author__ = 'Danny'


class Query(BaseQuery):
    def first_or_404(self):           # 重写
        rv = self.first()
        if not rv:
            raise NotFound()
        return rv


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


db = SQLAlchemy(query_class=Query)


class Base(db.Model):
    __abstract__ = True
    def __init__(self):
        pass

    def __getitem__(self, item):
        return getattr(self, item)









