from flask import Flask
from flask import jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import os
from pprint import pprint

from data import db_session
# Importing utils
from utils import converter, validation

# Importing all models to work correctly in app.py
from data.transport_type import TransportTypes
from data.regions_to_couriers import CouriersToRegions
from data.orders import Orders
from data.regions import Regions
from data.delivery import Delivery
from data.couriers import Couriers

from data.schemas import *

app = Flask(__name__)

# 1) POST /couriers


@app.route('/couriers', methods=['POST'])
def get_couriers():
    data = request.get_json()
    couriers_list = data['data']

    db_sess = db_session.create_session()
    validation_error = {"validation_error": {
        "couriers": []
        }
        }

    valid_couriers = []
    for courier_json in couriers_list:

        if validation.validate_courier_json(courier_json, db_sess):
            courier_json['working_hours'] = converter.convert_wh_hours_to_str(
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
            if db_sess.query(Regions).filter(Regions.region_code == region_name).first(
            ) is None and region_name not in added_regions:
                reg = Regions(region_name)
                db_sess.add(reg)
                # db_sess.commit()
                added_regions.append(reg)
            elif db_sess.query(Regions).filter(Regions.region_code == region_name).first() is not None:
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


# 2) PATCH /couriers/$courier_id
@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
def patch_couriers(courier_id):
    return jsonify(['Okay, PATCH `EM ALL', courier_id])


# 3) POST /orders
@app.route('/orders', methods=['POST'])
def set_orders():
    # --------------------------------------------------------------------------
    data = request.get_json()
    orders_list = data['data']

    db_sess = db_session.create_session()
    validation_error = {"validation_error": {
        "orders": []
        }
        }

    valid_orders = []
    for order_json in orders_list:

        if validation.validate_courier_json(courier_json, db_sess):
            courier_json['working_hours'] = converter.convert_wh_hours_to_str(
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
            if db_sess.query(Regions).filter(Regions.region_code == region_name).first(
            ) is None and region_name not in added_regions:
                reg = Regions(region_name)
                db_sess.add(reg)
                # db_sess.commit()
                added_regions.append(reg)
            elif db_sess.query(Regions).filter(Regions.region_code == region_name).first() is not None:
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


# 4) POST /orders/assign
@app.route('/orders/assign', methods=['POST'])
def assign_orders():
    return jsonify(['Okay, ORDERS is ASSIGMENTING'])


# 5) POST /orders/complete
@app.route('/orders/complete', methods=['POST'])
def complete_order():
    return jsonify(['Okay, ORDER COMPLETED'])

# 6) GET /couriers/$courier_id


@app.route('/couriers/<int:courier_id>', methods=['GET'])
def get_courier_info(courier_id):
    db_sess = db_session.create_session()
    courier = db_sess.query(Couriers).filter(
        Couriers.courier_id == courier_id).first()
    schema_courier = CouriersSchema()
    json_courier = schema_courier.dump(courier)
    return make_response(jsonify(json_courier))


client = app.test_client()

app.config['SECRET_KEY'] = os.getenv('KEY')

# SCHEMAS FOR (DE)SERIALIZING DATA
couriers_schema = CouriersSchema()
regions_schema = RegionsSchema()
type_schema = TransportTypesSchema()


def main():
    # Preparing db and run app
    db_session.global_init_sqlite('db.sqlite')
    app.run()


if __name__ == '__main__':
    main()
