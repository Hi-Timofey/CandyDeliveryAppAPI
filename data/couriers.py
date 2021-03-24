import sqlalchemy as sa
from sqlalchemy import orm
from .transport_type import TransportTypes

import re
from cerberus import Validator
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

    def __repr__(self):
        return 'Courier(id="{}", type="{}", working_hours="{}", regions="{}")'.format(
            self.courier_id, self.courier_type, self.working_hours, self.regions)

    @staticmethod
    def validate_regions(regions: list) -> bool:
        if not isinstance(regions, list):
            return False
        for r in regions:
            try:
                if isinstance(r, bool) or not isinstance(r, int):
                    return False
                if r <= 0:
                    return False
                if regions.count(r) > 1:
                    return False
            except TypeError as te:
                return False

        return True

    @staticmethod
    def validate_wh(working_hours: list) -> bool:
        s = re.compile('^[0-2]{1}[0-9]{1}:[0-9]{2}-[0-2]{1}[0-9]{1}:[0-9]{2}$')
        if not (isinstance(
                working_hours, list) and len(working_hours) > 0):
            return False

        for wh in working_hours:
            try:
                assert s.match(wh)
                period = wh.split('-')
                time_from = datetime.time.fromisoformat(period[0])
                time_to = datetime.time.fromisoformat(period[1])
            except ValueError as ve:
                return False
            except AttributeError as ae:
                return False
            except BaseException as be:
                raise ValueError(be)

            if not time_from < time_to:
                return False
        return True

    @staticmethod
    def validate_courier_json(courier_json: dict, db) -> bool:
        cj_schema = {
            'courier_id': {
                'required': True,
                'type': 'integer'},
            'courier_type': {
                'required': True,
                'type': 'string',
                'regex': '^[a-zA-Z]+$'},
            'regions': {
                'type': 'list',
                'required': True,
                'minlength': 0,
                'schema': {
                    'type': 'integer',
                    'min': 0}},
            'working_hours': {'type': 'list'}}
        cour_valid = Validator(cj_schema)

        if cour_valid.validate(courier_json):
            try:
                i = courier_json['courier_id']
                wh = courier_json['working_hours']
                r = courier_json['regions']
                types = courier_json['courier_type']

                query_type = db.query(
                    TransportTypes.type_name).filter(
                    TransportTypes.type_name.like(types))
                query_id = db.query(Couriers).filter(
                    Couriers.courier_id == i).first()

                return query_id is None and Couriers.validate_wh(
                    wh) and Couriers.validate_regions(r) and (types,) in query_type
            except BaseException as be:
                raise ValueError('Something went wrong - ' + str(be))
        else:
            return False  # cour_valid.errors
