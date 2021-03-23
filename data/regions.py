import sqlalchemy as sa
from sqlalchemy import orm

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .db_session import SqlAlchemyBase


class Regions(SqlAlchemyBase):
    __tablename__ = 'regions'

    region_id = sa.Column(sa.Integer,
                          primary_key=True, autoincrement=True)

    region_code = sa.Column(sa.Integer, nullable=False)

    regions_orders = orm.relation('Orders', back_populates='regions')


# class RegionsSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = Regions
#         include_relationships = True
#         load_instance = True
