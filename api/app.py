# -*- coding: utf-8 -*-
from flask import Flask
from flask import jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy

from data import db_session

# Importing all models to work correctly in app.py
from data.transport_type import TransportTypes
from data.regions_to_couriers import CouriersToRegions
from data.orders import Orders
from data.regions import Regions
from data.delivery import Delivery
from data.couriers import *


# Other packages
import os
from pprint import pprint
import datetime

app = Flask(__name__)


@app.route('/couriers', methods=['POST'])
def post_couriers():
    '''
    1) POST /couriers
    '''
    try:
        data = request.get_json()
        couriers_list = data['data']
    except BaseException as be:
        return make_response(
            jsonify({'validation_error': 'wrong json data'}), 400)

    db_sess = db_session.create_session()

    validation_error = {"validation_error": {
        "couriers": []
    }
    }

    valid_couriers = []
    for courier_json in couriers_list:

        if Couriers.validate_courier_json(courier_json, logger=app.logger):
            courier_json['working_hours'] = convert_wh_hours_to_str(
                courier_json['working_hours'])
            courier_json['courier_type'] = db_sess.query(
                TransportTypes).filter(
                    TransportTypes.type_name
                    == courier_json['courier_type']).first()
        else:
            validation_error["validation_error"]['couriers'].append(
                {'id': courier_json['courier_id']})
            continue

        added_regions = []
        regions = []
        for region_name in courier_json['regions']:
            if db_sess.query(Regions).filter(Regions.region_code ==
                                             region_name).first(
            ) is None and region_name not in added_regions:
                reg = Regions(region_name)
                db_sess.add(reg)
                # db_sess.commit()
                added_regions.append(reg)
            else:
                reg = db_sess.query(Regions).filter(
                    Regions.region_code == region_name).first()
                regions.append(reg)

        courier = Couriers()
        courier.courier_id = courier_json['courier_id']
        courier.courier_type_id = courier_json['courier_type'].type_id
        courier.regions = added_regions + regions
        courier.working_hours = courier_json['working_hours']
        valid_couriers.append(courier)

    if len(validation_error["validation_error"]['couriers']) != 0:
        return make_response(jsonify(validation_error), '400 Bad Request')

    response = {'couriers': []}
    app.logger.info(f'Adding the following Couriers:')
    for cour in valid_couriers:
        app.logger.info(cour)
        db_sess.add(cour)
        response['couriers'].append({"id": cour.courier_id})
        db_sess.commit()

    return make_response(jsonify(response), '201 Created')


@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
def patch_couriers(courier_id):
    '''
    2) PATCH /couriers/$courier_id
    '''
    if isinstance(courier_id, int):
        if courier_id > 0:
            data = request.get_json()
            db_sess = db_session.create_session()

            if Couriers.validate_patch(data, db_sess, logger=app.logger):

                cour = db_sess.query(Couriers).filter(
                    Couriers.courier_id.like(courier_id)).first()

                if cour:
                    app.logger.info(
                        f'Changing {cour} with following params:\n{data.keys()}')
                    for key in data:
                        # TODO Bad perfomance, change with getattr/setattr(?) or
                        # property function
                        if isinstance(data[key], str):

                            new_type = db_sess.query(TransportTypes).filter(
                                TransportTypes.type_name == data[key]).first()
                            if new_type:
                                cour.change_cour_type(new_type, db_sess)

                        elif isinstance(data[key][0], int):

                            new_regions = data[key]
                            cour.change_cour_regions(new_regions, db_sess)

                        elif isinstance(data[key][0], str):

                            new_working_hours = data[key]
                            cour.change_cour_work_hours(
                                new_working_hours, db_sess)

                    return make_response(
                        jsonify(
                            Couriers.make_courier_response(
                                cour)),
                        '200 OK')
                else:
                    app.logger.info(f'No courier with id {courier_id}')
                    return '', '404 Not found'

    app.logger.info(f'Requets courier with id {courier_id} is bad')
    return '', '400 Bad request'


@ app.route('/orders', methods=['POST'])
def set_orders():
    '''
    3) POST /orders
    '''
    try:
        data = request.get_json()
        orders_list = data['data']
    except BaseException as be:
        app.logger.exception(f'Wrong JSON data passed: {be}')
        return make_response('400 Bad request')

    db_sess = db_session.create_session()
    ve = False
    validation_error = {"validation_error": {
        "orders": []
    }
    }

    valid_orders = []
    for order_json in orders_list:

        if Orders.validate_order_json(order_json, db_sess, logger=app.logger):
            if ve:
                continue
            order = Orders()
            order.order_id = order_json['order_id']
            order.weight = order_json['weight']

            query_region = db_sess.query(Regions).filter(
                Regions.region_code == order_json['region']).first()
            if query_region is None:
                reg = Regions(region_code=order_json['region'])
            else:
                reg = query_region

            db_sess.add(reg)

            order.region = reg
            order.delivery_time = convert_wh_hours_to_str(
                order_json['delivery_hours'])

            valid_orders.append(order)
        else:
            try:
                validation_error["validation_error"]['orders'].append(
                    {'id': order_json['order_id']}
                )
            except KeyError as ke:
                validation_error["validation_error"]['schema_error'] = order_json
            db_sess.rollback()
            ve = True
            continue

    if ve:
        app.logger.info(f'Passes not valid data: {validation_error}')
        return make_response(jsonify(validation_error), '400 Bad request')
    else:
        response = {'orders': []}

        for order in valid_orders:
            db_sess.add(order)
            response['orders'].append({"id": order.order_id})
            db_sess.commit()
        return make_response(jsonify(response), '201 Created')


@ app.route('/orders/assign', methods=['POST'])
def assign_orders():
    '''
    4) POST /orders/assign
    '''
    data = request.get_json()
    db_sess = db_session.create_session()

    if data is not None:
        if Couriers.validate_assigment(data):
            courier_id = data['courier_id']

            cour = db_sess.query(Couriers).filter(
                Couriers.courier_id == courier_id).first()

            if cour is not None:
                if not cour.is_working():

                    regions = [reg.region_id for reg in cour.regions]

                    orders = db_sess.query(Orders).filter(
                        Orders.order_complete_time == None).filter(
                            Orders.delivery_id == None).filter(
                                Orders.weight <= cour.courier_type.type_weight,
                                Orders.region_id.in_(regions)).all()

                    for_deliver = []
                    for order in orders:
                        if cour.could_he_take(order):
                            for_deliver.append(order)

                    if len(for_deliver) > 0:
                        response = {
                            "orders": [],
                            "assign_time": "2021-01-10T09:32:14.42Z"
                        }

                        delivery = Delivery()
                        for order in for_deliver:
                            response['orders'].append({'id': order.order_id})
                            # --- DB ---

                        delivery.delivery_courier = cour
                        delivery.assigned_courier_type_id = cour.courier_type_id
                        delivery.assigned_courier_type = cour.courier_type
                        assign_time = datetime.datetime.now()
                        delivery.assign_time = assign_time
                        delivery.orders_in_delivery = for_deliver
                        app.logger.info(
                            f'{cour} got {delivery} with {for_deliver}')
                        db_sess.add(delivery)
                        db_sess.commit()
                        # --- END ---

                        response['assign_time'] = assign_time.isoformat()[
                            :-4] + "Z"
                        return make_response(jsonify(response), '200 OK')
                    return make_response(jsonify({'orders': []}), '200 OK')
                else:
                    try:
                        current_delivery = cour.get_current_delivery()
                        app.logger.info(
                            f'Courier {courier_id} have {current_delivery}')
                        orders_list = db_sess.query(
                            Orders.order_id).filter(
                                Orders.delivery_id
                                == current_delivery.delivery_id).filter(
                                    Orders.order_complete_time == None
                        ).all()
                        response = {
                            'orders':
                            [{'id': order.order_id} for order in orders_list],
                            'assign_time': current_delivery.get_str_assign_time()}
                        return make_response(jsonify(response), '200 OK')
                    except BaseException:
                        app.logger.exception(
                            '/assign can`t show any information.')
                        return '', '400 Bad request'
    return '', '400 Bad request'


@ app.route('/orders/complete', methods=['POST'])
def complete_order():
    '''
    5) POST /orders/complete
    '''
    data = request.get_json()
    db_sess = db_session.create_session()
    if data:
        if Orders.validate_complete(data, db_sess, logger=app.logger):
            order = db_sess.query(Orders).filter(
                Orders.order_id == data['order_id']).first()

            response = {'order_id': order.order_id}
            complete_time = datetime.datetime.fromisoformat(
                data['complete_time'][:22] + '0')

            if not order.is_completed():
                order.order_complete_time = complete_time
            else:
                return make_response(jsonify(response), '200 OK')

            db_sess.add(order)

            delivery = order.delivery
            if delivery.is_completed():
                delivery.delivery_complete_time = complete_time

            db_sess.add(delivery)
            db_sess.commit()
            return make_response(jsonify(response), '200 OK')
    return '', '400 Bad request'


@ app.route('/couriers/<int:courier_id>', methods=['GET'])
def get_courier_info(courier_id):
    '''
    6) GET /couriers/$courier_id
    '''
    db_sess = db_session.create_session()
    if courier_id >= 1:

        courier = db_sess.query(Couriers).filter(
            Couriers.courier_id == courier_id).first()

        if courier:
            delivery = db_sess.query(Delivery)\
                .filter(Delivery.delivery_complete_time is not None)\
                .filter(Delivery.courier_id == courier_id).all()

            # Counting Earnings of courier
            earnings = 0
            for d in delivery:
                earnings += d.count_earning()
                courier.earnings = earnings

            add_response = {'earnings': earnings}
            # Counting rationg of courier
            if len(delivery) > 0:
                regions_avg = Regions.count_avg_time_from_orders(delivery)
                if len(regions_avg) != 0:
                    rating = Couriers.count_rating_from_regions_avg(
                        regions_avg)

                    courier.rating = rating
                    add_response['rating'] = rating

            db_sess.add(courier)
            response = Couriers.make_courier_response(
                courier, **add_response)
            db_sess.commit()
            return make_response(jsonify(response), 200)
        else:
            app.logger.info(f'No courier with id {courier_id}')

    return '', '404 Not found'


def main(debug=False):
    # Preparing db and run app
    db_session.global_init_sqlite('db.sqlite')
    app.config.from_envvar('API_CONFIG')
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main(debug=True)
