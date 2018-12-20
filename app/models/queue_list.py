"""
 Created by Danny on 2018/12/14
"""
from app.models.base import db
import json
from app.libs.helper import get_current_date
__author__ = 'Danny'


class QueueList(db.Model):
    __tablename__ = 'queue_list'

    id = db.Column(db.Integer, primary_key=True)
    queue_name = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue())
    data = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    @staticmethod
    def add_queue(queue_name, data=None):
        model_queue = QueueList()
        model_queue.queue_name = queue_name
        if data:
            model_queue.data = json.dumps(data)

        model_queue.created_time = model_queue.updated_time = get_current_date()
        with db.auto_commit():
            db.session.add(model_queue)
        return True









