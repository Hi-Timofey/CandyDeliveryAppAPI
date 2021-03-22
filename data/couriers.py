import sqlalchemy as sa
from sqlalchemy import orm

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import datetime
from .db_session import SqlAlchemyBase


class Couriers(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = sa.Column(sa.Integer,
                           primary_key=True, autoincrement=True)

    courier_type = sa.Column(sa.String, nullable=False)

    working_hours = sa.Column(sa.String, nullable=False)

    rating = sa.Column(sa.Float, nullable=False, default=0)

    earnings = sa.Column(sa.Integer, nullable=False, default=0)

    regions = orm.relation("Regions",
                           secondary='regions_to_couriers',
                           backref='couriers')


# class CouriersSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = Couriers
#         include_relationships = True
#         load_instance = True
