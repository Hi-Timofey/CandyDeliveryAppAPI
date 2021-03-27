import sqlalchemy as sa
from sqlalchemy import orm

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .db_session import SqlAlchemyBase


class Regions(SqlAlchemyBase):
    __tablename__ = 'regions'

    region_id = sa.Column(sa.Integer,
                          primary_key=True, autoincrement=True)

    region_code = sa.Column(sa.Integer, nullable=False, unique=True)

    regions_orders = orm.relation('Orders', back_populates='region')

    def __init__(self, region_code):
        self.region_code = region_code

    def __repr__(self):
        return f'REG(id={self.region_id}, code={self.region_code})'

    def create(self, db_session):
        db_session.add(self)
        db_session.commit()
        return self

    def count_avg_time_from_orders(delivery, type_='list'):
        if type_ not in ['list', 'dict']:
            raise ValueError('Wrong output type required')

        summ = {}
        count = {}

        for deliv in delivery:
            if deliv.delivery_complete_time is not None:
                orders_delivery_time = deliv.count_orders_delivery_time()
                for order in orders_delivery_time:
                    region = order.region
                    if region not in summ.keys():
                        summ[region] = orders_delivery_time[order]
                        count[region] = 1

                    else:
                        average_td[region] += ord_dev_time[order]
                        region_count[region] += 1

        if type_ == 'list':
            answer = []
            for region in summ:
                answer.append(summ[region] / count[region])

        elif type_ == 'dict':
            answer = {}
            for region in summ:
                answer[region] = summ[region] / count[region]
        return answer
