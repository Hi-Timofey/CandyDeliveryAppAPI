import sqlalchemy as sa
from sqlalchemy import orm

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .db_session import SqlAlchemyBase


class RegionsToCouriers(SqlAlchemyBase):
    __tablename__ = 'regions_to_couriers'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)

    region_id = sa.Column('regions', sa.Integer,
                          sa.ForeignKey('regions.region_id'))

    courier_id = sa.Column(
        'couriers', sa.Integer, sa.ForeignKey(
            'couriers.courier_id'))
