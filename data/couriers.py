import sqlalchemy as sa
from sqlalchemy import orm

from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields


import datetime
from .db_session import SqlAlchemyBase


class Couriers(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = sa.Column(sa.Integer,
                           primary_key=True, autoincrement=True)

    courier_type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('transport_types.type_id'),
        nullable=False)

    courier_type = orm.relation(
        'TransportTypes',
        back_populates='couriers_with_type',
        viewonly=True)

    working_hours = sa.Column(sa.String, nullable=False)

    rating = sa.Column(sa.Float, nullable=False, default=0)

    earnings = sa.Column(sa.Integer, nullable=False, default=0)

    regions = orm.relation("Regions",
                           secondary='couriers_to_regions',
                           backref='couriers')

    courier_delivery = orm.relation(
        'Delivery', back_populates='delivery_courier')

# TODO: Refractor to another dir and separeted file for this class


class CouriersSchema(SQLAlchemySchema):
    class Meta:
        model = Couriers
        load_instance = True

    courier_id = auto_field()
    working_hours = auto_field()
