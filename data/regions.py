import sqlalchemy as sa
from sqlalchemy import orm

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .db_session import SqlAlchemyBase


# RegionsToCouriers = sqlalchemy.Table(
#     'regions_to_couriers',
#     SqlAlchemyBase.metadata,
#     sqlalchemy.Column('regions', sqlalchemy.Integer,
#                       sqlalchemy.ForeignKey('regions.region_id')),
#     sqlalchemy.Column('couriers', sqlalchemy.Integer,
#                       sqlalchemy.ForeignKey('couriers.courier_id'))
# )

class Regions(SqlAlchemyBase):
    __tablename__ = 'regions'

    region_id = sa.Column(sa.Integer,
                          primary_key=True, autoincrement=True)

    region_code = sa.Column(sa.Integer, nullable=False)


# class RegionsSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = Regions
#         include_relationships = True
#         load_instance = True
