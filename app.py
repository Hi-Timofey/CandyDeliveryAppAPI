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
def get_couriers():
    '''
    1) POST /couriers
    '''
    data = request.get_json()
    couriers_list = data['data']

    db_sess = db_session.create_session()
    validation_error = {"validation_error": {
        "couriers": []
        }
        }

    valid_couriers = []
    for courier_json in couriers_list:

        if Couriers.validate_courier_json(courier_json, db_sess):
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
        return make_response(jsonify(validation_error), 400)

    response = {'couriers': []}
    for cour in valid_couriers:
        db_sess.add(cour)
        response['couriers'].append({"id": cour.courier_id})
    db_sess.commit()

    return make_response(jsonify(response), 201)


@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
def patch_couriers(courier_id):
    '''
    2) PATCH /couriers/$courier_id
    '''
    breakpoint()
    if isinstance(courier_id, int):
        if courier_id > 0:
            data = request.get_json()
            db_sess = db_session.create_session()

            if Couriers.validate_patch(data):

                cour = db_sess.query(Couriers).filter(
                        Couriers.courier_id.like(courier_id)).first()

                for key in data:
                    # TODO Bad perfomance
                    if isinstance(data[key], str):
                        # cour type
                        new_type = db_sess.query(TransportTypes).filter(
                            TransportTypes.type_name == data[key]).first()
                        if new_type:
                            cour.change_cour_type(new_type, db_sess)
                    elif isinstance(data[key], str) and \
                            isinstance(data[key][0], int):
                        # region
                        new_regions = data[key]
                        cour.change_cour_regions(new_regions, db_sess)
                    else:
                        new_working_hours = data[key]
                        cour.change_cour_work_hours(new_working_hours, db_sess)

            return make_response(
                jsonify(Couriers.make_courier_response(cour)), 201)
    return '', '400 Bad request'


@ app.route('/orders', methods=['POST'])
def set_orders():
    '''
    3) POST /orders
    '''
    data = request.get_json()
    orders_list = data['data']

    db_sess = db_session.create_session()
    ve = False
    validation_error = {"validation_error": {
        "orders": []
        }
        }

    valid_orders = []
    for order_json in orders_list:

        if Orders.validate_order_json(order_json, db_sess):
            if ve:
                continue
            order = Orders()
            order.order_id = order_json['order_id']
            order.weight = order_json['weight']

            reg = Regions(region_code=order_json['region'])

            order.region = reg
            order.delivery_time = convert_wh_hours_to_str(
                order_json['delivery_hours'])

            valid_orders.append(order)
        else:
            validation_error["validation_error"]['orders'].append(
                {'id': order_json['order_id']}
            )
            ve = True
            continue

    if ve:
        return make_response(jsonify(validation_error), 400)
    else:
        response = {'orders': []}

        for order in valid_orders:
            db_sess.add(order)
            response['orders'].append({"id": order.order_id})
        db_sess.commit()
        return make_response(jsonify(response), 201)


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

            if cour is not None and not cour.is_working():

                regions = [reg.region_id for reg in cour.regions]

                orders = db_sess.query(Orders).filter(
                    Orders.weight <= cour.courier_type.type_weight,
                    Orders.region_id.in_(regions)
                ).all()

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
                    db_sess.add(delivery)
                    db_sess.commit()
                    # --- END ---

                    response['assign_time'] = assign_time.isoformat()[
                                                                    :-4] + "Z"
                    return make_response(jsonify(response), 201)
                return make_response(jsonify({'orders': []}), 201)
            else:
                current_delivery = cour.get_current_delivery()
                orders_list = db_sess.query(
                    Orders.order_id).filter(
                    Orders.delivery_id == current_delivery.delivery_id).all()
                breakpoint()
                response = {
                    'orders':
                    [{'id': order.order_id} for order in orders_list],
                    'assign_time': current_delivery.get_str_assign_time()}
                return make_response(jsonify(response), 201)
    return '', '400 Bad request'


@ app.route('/orders/complete', methods=['POST'])
def complete_order():
    '''
    5) POST /orders/complete
    '''
    data = request.get_json()
    db_sess = db_session.create_session()
    if data:
        breakpoint()
        if Orders.validate_complete(data, db_sess):
            order = db_sess.query(Orders).filter(
                Orders.order_id == data['order_id']).first()

            response = {'order_id': order.order_id}
            complete_time = datetime.datetime.fromisoformat(
                data['complete_time'][: -1] + '0')

            if order.is_completed():
                order.order_complete_time = complete_time
            else:
                return make_response(jsonify(response), 200)

            db_sess.add(order)

            breakpoint()
            delivery = order.delivery
            if delivery.is_completed():
                delivery.delivery_complete_time = complete_time

            db_sess.add(delivery)
            db_sess.commit()
            return make_response(jsonify(response), 200)
    return '', '400 Bad request'


@ app.route('/couriers/<int:courier_id>', methods=['GET'])
def get_courier_info(courier_id):
    '''
    6) GET /couriers/$courier_id
    '''
    db_sess = db_session.create_session()
    courier = db_sess.query(Couriers).filter(
        Couriers.courier_id == courier_id).first()
    response = Couriers.make_courier_response(courier)
    return make_response(jsonify(response))


client = app.test_client()

app.config['SECRET_KEY'] = os.getenv('KEY')


def main():
    # Preparing db and run app
    db_session.global_init_sqlite('db.sqlite')
    app.run()


if __name__ == '__main__':
    main()
