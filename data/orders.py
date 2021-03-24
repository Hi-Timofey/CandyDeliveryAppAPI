import sqlalchemy as sa
from sqlalchemy import orm
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

import datetime
from .db_session import SqlAlchemyBase
from cerberus import Validator
from .couriers import validate_wh


class Orders(SqlAlchemyBase):
    __tablename__ = 'orders'

    order_id = sa.Column(sa.Integer,
                         primary_key=True, autoincrement=True)

    weight = sa.Column(sa.Float, nullable=False)

    region_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('regions.region_id'),
        nullable=False)

    region = orm.relation("Regions", backref='orders')

    delivery_time = sa.Column(sa.String, nullable=False)

    order_complete_time = sa.Column(sa.DateTime, nullable=True)

    # delivery_id = None

    def __repr__(self):
        return f'<Order id={self.order_id}>'

    @staticmethod
    def validate_order_json(order_json, db):
        schema = {'order_id': {
                'required': True,
            'type': 'integer', 'min': 1},
                  'weight': {
                'required': True,
                      'type': 'float', 'min': 0.01, 'max': 50.0},
                  'region': {
                'required': True,
                      'type': 'integer', 'min': 1},
            'delivery_hours': {'check_with': validate_wh}}
        v = Validator(schema)
        if v.validate(order_json):
            i = order_json['order_id']
            query_id = db.query(Orders).filter(
                Orders.order_id == i).first()
            return query_id is None
        else:
            return False
