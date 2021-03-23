import sqlalchemy as sa
from sqlalchemy import orm

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .db_session import SqlAlchemyBase


class CouriersToRegions(SqlAlchemyBase):
    __tablename__ = 'couriers_to_regions'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)

    region_id = sa.Column('regions', sa.Integer,
                          sa.ForeignKey('regions.region_id'))

    courier_id = sa.Column(
        'couriers', sa.Integer, sa.ForeignKey(
            'couriers.courier_id'))
