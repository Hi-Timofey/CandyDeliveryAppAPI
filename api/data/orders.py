import sqlalchemy as sa
from sqlalchemy import orm
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

import datetime
from .db_session import SqlAlchemyBase
from .db_session import create_session
from cerberus import Validator
from .couriers import validate_wh, convert_wh_hours_to_time, convert_str_hours_to_wh
from .regions import Regions


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
        if self.order_complete_time:
            return f'<Order {self.order_id} |COMPLETED|)'
        return f'<Order {self.order_id} >'

    def count_delivery_time_sec(self, db) -> int:
        pass

    def is_completed(self):
        return self.order_complete_time is not None

    def get_delivery_time(self) -> list:
        string = self.delivery_time
        wh = convert_str_hours_to_wh(string)
        return convert_wh_hours_to_time(wh)

    @staticmethod
    def delivery_time_of(order) -> list:
        string = order.delivery_time
        wh = convert_str_hours_to_wh(string)
        return convert_wh_hours_to_time(wh)

    @staticmethod
    def validate_complete(complete_json, db, logger=None):
        schema = {
            'order_id': {
                'type': 'integer', 'min': 1}, 'courier_id': {
                'type': 'integer', 'min': 1}, 'complete_time': {
                'regex': r'^(\d{4})-(\d{2})-(\d{2})T(\d){2}:(\d){2}:(\d){2}.(\d{2,6})Z$'}}

        v = Validator(schema)
        if v.validate(complete_json):
            order = db.query(Orders).filter(
                Orders.order_id == complete_json['order_id']).first()
            if order:
                delivery = order.delivery
                if delivery:
                    if delivery.delivery_courier.courier_id \
                            == complete_json['courier_id']:
                        withoutz_string = complete_json['complete_time'][:22]
                        complete_time = datetime.datetime.fromisoformat(
                            withoutz_string + '0')

                        period_time = Orders.delivery_time_of(order)
                        breakpoint()
                        if not any(
                            [p[0] < complete_time.time() < p[1]
                             for p in period_time]):
                            if logger:
                                logger.info(
                                    f'Complete time{complete_time} is not match delivery time of order: {order}')
                            return False

                        breakpoint()
                        if delivery.assign_time.time() < complete_time.time():
                            orders = delivery.orders_in_delivery
                            for order in orders:
                                if order.order_complete_time:
                                    if order.order_complete_time.time() > \
                                            complete_time.time():
                                        if logger:
                                            logger.info(
                                                f'Wrong completion time: {order} AND {complete_time}')
                                        return False
                            return True
        elif logger:
            logger.info(f'Bad data: {v.errors}')
        return False

    @staticmethod
    def validate_order_json(order_json, logger=None):
        dh_s = {
            'empty': False,
            'type': 'list',
            'schema': {
                'type': 'string',
                'regex': '^[0-2]{1}[0-9]{1}:[0-5]{1}[0-9]{1}-[0-2]{1}[0-9]{1}:[0-5]{1}[0-9]{1}$'

            }
        }
        schema = {'order_id': {
            'required': True,
            'type': 'integer', 'min': 1},
            'weight': {
            'required': True,
            'type': 'float', 'min': 0.01, 'max': 50.0},
            'region': {
                'required': True,
            'type': 'integer', 'min': 1},
            'delivery_hours': dh_s}
        v = Validator(schema)
        if v.validate(order_json):
            i = order_json['order_id']
            wh = order_json['delivery_hours']
            db = create_session()
            query_id = db.query(Orders).filter(
                Orders.order_id == i).first()

            answer = query_id is None and validate_wh(wh)

            return query_id is None and validate_wh(wh)
        else:
            if logger:
                logger.info(v.errors)
            return False
