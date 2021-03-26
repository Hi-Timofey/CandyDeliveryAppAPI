import sqlalchemy as sa
from sqlalchemy import orm
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

import datetime
from .db_session import SqlAlchemyBase
from cerberus import Validator
from .couriers import validate_wh, convert_wh_hours_to_time, convert_str_hours_to_wh


class Orders(SqlAlchemyBase):
    __tablename__ = 'orders'

    order_id = sa.Column(sa.Integer,
                         primary_key=True, autoincrement=True)

    weight = sa.Column(sa.Float, nullable=False)

    region_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('regions.region_id'),
        nullable=False)

    region = orm.relation("Regions", back_populates='regions_orders')

    delivery_time = sa.Column(sa.String, nullable=False)

    order_complete_time = sa.Column(sa.DateTime, nullable=True)

    delivery_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('delivery.delivery_id'),
        nullable=True)

    delivery = orm.relation(
        'Delivery',
        back_populates='orders_in_delivery')

    def __repr__(self):
        return f'ORDer(id={self.order_id}, time_to={self.delivery_time})'


    def count_delivery_time_sec(self, db) -> int:
        pass


    def is_completed(self):
        return self.order_complete_time is not None

    def get_delivery_time(self) -> list:
        string = self.delivery_time
        wh = convert_str_hours_to_wh(string)
        return convert_wh_hours_to_time(wh)

    @staticmethod
    def validate_complete(complete_json, db):
        schema = {
            'order_id': {
                'type': 'integer', 'min': 1}, 'courier_id': {
                'type': 'integer', 'min': 1}, 'complete_time': {
                'regex': '^(\d{4})-(\d{2})-(\d{2})T(\d){2}:(\d){2}:(\d){2}.(\d{2,6})Z$'}}

        v = Validator(schema)
        if v.validate(complete_json):
            order = db.query(Orders).filter(
                Orders.order_id == complete_json['order_id']).first()
            if order:
                delivery = order.delivery
                if delivery:
                    if delivery.delivery_courier.courier_id \
                            == complete_json['courier_id']:
                        complete_time = datetime.datetime.fromisoformat(
                            complete_json['complete_time'][:-1] + '0')
                        if delivery.assign_time < complete_time:
                            orders = delivery.orders_in_delivery
                            for order in orders:
                                if order.order_complete_time:
                                    if order.order_complete_time > \
                                            complete_time:
                                        return False
                            return True
        return False

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
