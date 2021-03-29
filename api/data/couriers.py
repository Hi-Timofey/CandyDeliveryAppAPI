import sqlalchemy as sa
from sqlalchemy import orm
from .transport_type import TransportTypes
from .regions import Regions

import re
import json
from datetime import time
from cerberus import Validator
import datetime
from .db_session import SqlAlchemyBase
from .db_session import create_session


def convert_wh_hours_to_time(working_hours):
    answer = []
    for wh in working_hours:
        period = wh.split('-')
        time_from = time.fromisoformat(period[0])
        time_to = time.fromisoformat(period[1])
        answer.append([time_from, time_to])
    return answer


def convert_str_hours_to_wh(string_hours: list) -> str:
    answer = json.loads(string_hours)
    return answer


def convert_wh_hours_to_str(working_hours: list) -> str:
    answer = json.dumps(working_hours)
    return answer


def validate_wh(working_hours: list, *cerb) -> bool:

    if cerb != ():
        working_hours = cerb[0]

    s = re.compile(
        '^[0-2]{1}[0-9]{1}:[0-5]{1}[0-9]{1}-[0-2]{1}[0-9]{1}:[0-5]{1}[0-9]{1}$')
    if not (isinstance(
            working_hours, list) and len(working_hours) > 0):
        if cerb != ():
            cerb[-1](working_hours, 'type TypeError')
        return False

    for wh in working_hours:
        if not (isinstance(
                wh, str)):
            return False
        a = s.match(wh) is not None
        if not a:
            if cerb != ():
                cerb[-1](working_hours, 'RegExp Error')
            return False
        try:
            period = wh.split('-')
            time_from = datetime.time.fromisoformat(period[0])
            time_to = datetime.time.fromisoformat(period[1])
        except ValueError as ve:
            if cerb != ():
                cerb[-1](working_hours, ve)
            return False
        except AttributeError as ae:
            if cerb != ():
                cerb[-1](working_hours, ae)
            return False
        except BaseException as be:
            if cerb != ():
                cerb[-1](working_hours, ve)
            raise ValueError(be)

        if not time_from < time_to:
            if cerb != ():
                cerb[-1](working_hours, 'Time Error')
            return False
    return True


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

    # def __setattr__(self, name, value):
    #     self.__dict__[name] = value

    @staticmethod
    def count_rating_from_regions_avg(regions_avg) -> float:
        t = min(regions_avg)
        answer = (60*60 - min(t, 60*60))/(60*60) * 5
        return answer

    def get_courier_wh_list(self):
        return convert_str_hours_to_wh(self.working_hours)

    # TODO serialize courier rename
    @staticmethod
    def make_courier_response(courier, **kwargs):
        response = {}
        response["courier_id"] = courier.courier_id
        response["courier_type"] = courier.courier_type.type_name
        response["regions"] = [
            region.region_code for region in courier.regions]
        response["working_hours"] = convert_str_hours_to_wh(
            courier.working_hours)
        if kwargs:
            for key in kwargs:
                response[key] = kwargs[key]
        return response

    def get_current_delivery(self):
        ''' Return`s current delivery of courier
            ( Delivery he`s working on )
        '''
        for delivery in self.courier_delivery:
            if delivery.delivery_complete_time is None:
                return delivery
        return None

    def change_cour_work_hours(self, new_working_hours, db_sess):
        old_working_hours = self.get_courier_wh_list()
        if new_working_hours != old_working_hours:
            delivery = self.get_current_delivery()
            if delivery:
                for order in delivery.orders_in_delivery:
                    if not order.is_completed():
                        if not self.could_he_take(
                                order, at_time=new_working_hours):
                            delivery.orders_in_delivery.remove(order)
                            order.delivery_id = None

                if delivery.is_completed():
                    print('completed delivery')
                if len(delivery.orders_in_delivery) == 0:
                    db_sess.delete(delivery)
            self.working_hours = convert_wh_hours_to_str(new_working_hours)
            db_sess.add(self)
            db_sess.commit()

    def change_cour_regions(self, new_regions, db_sess):
        old_regions = {reg.region_code for reg in self.regions}
        new_regions = set(new_regions)
        if new_regions != old_regions:
            delivery = self.get_current_delivery()
            if delivery:
                for order in delivery.orders_in_delivery:
                    if order.region.region_code not in new_regions:
                        delivery.orders_in_delivery.remove(order)

                if delivery.is_completed():
                    print('completed delivery')
                if len(delivery.orders_in_delivery) == 0:
                    db_sess.delete(delivery)
                    db_sess.commit()

            exists_in_db = db_sess.query(
                Regions.region_code, Regions).filter(
                Regions.region_code.in_(new_regions)).all()
            exists_set = {r[0] for r in exists_in_db}
            not_exists_set = new_regions - exists_set
            self.regions = []
            for code, reg in exists_in_db:
                self.regions.append(reg)
            for ne in not_exists_set:
                new_reg = Regions(region_code=ne)
                self.regions.append(new_reg)

            db_sess.add(self)
            db_sess.commit()

    def change_cour_type(self, new_type: TransportTypes, db_sess):
        if new_type != self.courier_type:
            delivery = self.get_current_delivery()
            if delivery and delivery.assigned_courier_type != new_type:
                for order in delivery.orders_in_delivery:
                    if order.weight > new_type.type_weight and \
                            order.order_complete_time is None:
                        delivery.orders_in_delivery.remove(order)

                if delivery.is_completed():
                    print('completed delivery')
                if len(delivery.orders_in_delivery) == 0:
                    db_sess.delete(delivery)
                    db_sess.commit()
            self.courier_type = new_type
            self.courier_type_id = new_type.type_id
            db_sess.add(self)
            db_sess.commit()

    def is_working(self) -> bool:
        deliveries = self.courier_delivery
        for delivery in deliveries:
            if delivery.delivery_complete_time is None:
                return True
        return False

    def could_he_take(self, order, at_time=None) -> bool:

        if order.is_completed():
            raise ValueError('Trying to take/check completed order')
        if at_time:
            work_hours = convert_wh_hours_to_time(at_time)
        else:
            at_time = self.working_hours
            work_hours = convert_wh_hours_to_time(
                convert_str_hours_to_wh(
                    at_time))
        wh_order = order.get_delivery_time()

        for could in work_hours:
            for need in wh_order:
                a0, b0 = could
                a1, b1 = need
                if b0 <= a1 or b1 <= a0:
                    continue
                else:
                    return True

        return False

    def __repr__(self):
        return f'<Courier {self.courier_id}>'


    @staticmethod
    def validate_patch(json_data: dict, db_sess, logger=None) -> bool:
        if not isinstance(json_data, dict) or json_data == {}:
            return False
        working_hours_s = {
            'working_hours': {
                'empty': False,
                'type': 'list',
                'schema': {
                    'type': 'string',
                    'regex': '^[0-2]{1}[0-9]{1}:[0-5]{1}[0-9]{1}-[0-2]{1}[0-9]{1}:[0-5]{1}[0-9]{1}$'}}}

        courier_type_s = {
            'courier_type': {'type': 'string',
                             'regex': '^[a-zA-Z]+$'}
                        }
        regions_s = {'regions': {'type': 'list',
                                 'minlength': 0,
                                 'empty': False,
                                 'schema': {
                                     'type': 'integer',
                                     'min': 1
                                     }}
                     }
        v = Validator()
        if len(json_data) == 1:
            res = any([
                v.validate(json_data, regions_s),
                v.validate(json_data, working_hours_s),
                v.validate(json_data, courier_type_s)])
        elif len(json_data) == 2:
            res = any([
                v.validate(json_data, {**courier_type_s, **regions_s}),
                v.validate(json_data, {**working_hours_s, **regions_s}),
                v.validate(json_data, {**working_hours_s, **courier_type_s})])
        elif len(json_data) == 3:
            res = v.validate(
                json_data, {**courier_type_s, **working_hours_s, **regions_s})
        else:
            raise BaseException('wtf')

        if res:

            if 'working_hours' in json_data.keys():
                check_wh = validate_wh(json_data['working_hours'])
            else:
                check_wh = True

            if 'courier_type' in json_data.keys():
                check_type = TransportTypes.type_exist(
                    json_data['courier_type'], db_sess)
            else:
                check_type = True

            return check_wh and check_type
        else:
            if logger:
                if v.errors != {}:
                    logger.info(f'PATCH error: {v.errors}')
                else:
                    logger.info('PATCH error: ', "wrong input data")
            return False

    @ staticmethod
    def validate_assigment(json_data: dict) -> bool:
        schema = {
            'courier_id': {
                'required': True,
                'type': 'integer', 'min': 1}}
        v = Validator(schema)
        res = v.validate(json_data)
        return res

    @ staticmethod
    def validate_courier_json(courier_json: dict, logger=None) -> bool:
        cj_schema = {
            'courier_id': {
                'required': True,
                'type': 'integer', 'min': 1},
            'courier_type': {
                'required': True,
                'type': 'string',
                'regex': '^[a-zA-Z]+$'},
            'regions': {
                      'required': True,
                      'type': 'list',
                      'minlength': 0,
                      'empty': False,
                      'schema': {
                          'type': 'integer',
                          'min': 1
                          }
                      },
            'working_hours': {'type': 'list'}}
        cour_valid = Validator(cj_schema)
        db = create_session()

        if cour_valid.validate(courier_json):
            try:
                i = courier_json['courier_id']
                wh = courier_json['working_hours']
                r = courier_json['regions']
                types = courier_json['courier_type']

                query_type = db.query(
                    TransportTypes.type_name).filter(
                    TransportTypes.type_name.like(types)).first()[0]

                query_id = db.query(Couriers).filter(
                    Couriers.courier_id == i).first()

                return query_id is None and validate_wh(
                    wh) and types in query_type
            except TypeError as te:
                print(f'NO SUCH TYPE "{types}" of couriers')
                return False
            except BaseException as be:
                raise ValueError('Something went wrong - ' + str(be))
        else:
            if logger:
                logger.info(cour_valid.errors)
            return False
