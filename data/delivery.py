import sqlalchemy as sa
from sqlalchemy import orm

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import datetime
from .db_session import SqlAlchemyBase


class Delivery(SqlAlchemyBase):
    __tablename__ = 'delivery'

    delivery_id = sa.Column(sa.Integer,
                            primary_key=True, autoincrement=True)

    assign_time = sa.Column(sa.DateTime, nullable=False)

    delivery_complete_time = sa.Column(sa.DateTime, nullable=True)

    courier_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('couriers.courier_id'),
        nullable=False)
    delivery_courier = orm.relation(
        'Couriers', back_populates='courier_delivery')

    assigned_courier_type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('transport_types.type_id'),
        nullable=False)

    assigned_courier_type = orm.relation(
        'TransportTypes',
        viewonly=True)

    orders_in_delivery = orm.relation(
        'Orders', back_populates='delivery')

    def __repr__(self):
        if not self.delivery_complete_time:
            completion = '|NO|'
        else:
            completion = self.delivery_complete_time
        return 'Delivery(id={}, assigned_time={}, completed={})'.format(
            self.delivery_id, self.assign_time, completion)

    def get_str_assign_time(self):
        return self.assign_time.isoformat() + 'Z'
