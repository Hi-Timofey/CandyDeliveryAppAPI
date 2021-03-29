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

    def set_completed_time(self, db_sess):
        db_sess.query(Orders).filter(Orders.delivery == self).all()
        breakpoint()

    def count_earning(self) -> int:
        if self.delivery_complete_time:
            return self.assigned_courier_type.type_earn_coefficient * 500
        return 0

    def count_orders_delivery_time(self) -> dict:
        # TODO Need tests
        if self.is_completed():
            sorted_orders = sorted(
                self.orders_in_delivery,
                key=lambda o: o.order_complete_time)
            answer = {}
            for i, so in enumerate(sorted_orders):
                if i == 0:
                    result = so.order_complete_time - self.assign_time
                else:
                    result = so.order_complete_time - \
                        sorted_orders[i-1].order_complete_time
                seconds = result.seconds
                answer[so] = seconds
        else:
            raise ValueError(
                'Trying to count orders delivery time for not completed delivery')
        return answer

    def __repr__(self):
        if not self.delivery_complete_time:
            completion = '|NO|'
        else:
            completion = self.delivery_complete_time
        return '< Delivery {}: assigned_time={}, completed={} >'.format(
            self.delivery_id, self.assign_time, completion)

    def is_completed(self) -> bool:
        orders = self.orders_in_delivery
        for order in orders:
            if order.order_complete_time is None:
                return False
        orders = sorted(orders,key=lambda x: x.order_complete_time)
        self.delivery_complete_time = orders[-1].order_complete_time
        return True

    def get_str_assign_time(self):
        return self.assign_time.isoformat()[:22] + 'Z'
