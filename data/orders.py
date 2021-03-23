import sqlalchemy as sa
from sqlalchemy import orm
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

import datetime
from .db_session import SqlAlchemyBase


class Orders(SqlAlchemyBase):
    __tablename__ = 'orders'

    order_id = sa.Column(sa.Integer,
                         primary_key=True, autoincrement=True)

    weight = sa.Column(sa.Float, nullable=False)

    region_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('regions.region_id'),
        nullable=False)

    regions = orm.relation("Regions", backref='orders')

    delivery_hours = sa.Column(sa.String, nullable=False)

    complete_time = sa.Column(sa.DateTime, nullable=True)

    # delivery_id = None

    def __repr__(self):
        return f'<Order id={self.id}>'
