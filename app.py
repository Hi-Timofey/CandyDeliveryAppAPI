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

from data.couriers import CouriersSchema

app = Flask(__name__)

client = app.test_client()

app.config['SECRET_KEY'] = os.getenv('KEY')


# SCHEMAS FOR (DE)SERIALIZING DATA
couriers_schema = CouriersSchema()


# 1) POST /couriers
@app.route('/couriers', methods=['POST'])
def get_couriers():
    data = request.get_json()
    couriers_list = data['data']

    db_sess = db_session.create_session()
    for courier_json in couriers_list:

        if validation.validate_courier_json(courier_json):
            courier_json['working_hours'] = converter.convert_wh_hours_to_str(
                courier_json['working_hours'])
        else:
            return jsonify(['NOPE'])

        added_regions = []
        for region_name in courier_json['regions']:
            if db_sess.query(Regions).filter(Regions.region_code == region_name).first(
            ) is None and region_name not in added_regions:
                print(f'creating region with code "{region_name}"...')
                breakpoint()
                reg = Regions(region_name)
                db_sess.add(reg)
                added_regions.append(reg)

        breakpoint()
        if not courier_json['courier_type'] not in ['foot','bike','car']:
            return jsonify(['NOPE'])
        courier = couriers_schema.load(courier_json, session=db_sess)

        print(
            'COURIER:',
            # courier_id,
            # courier_type,
            # regions,
            # working_hours,
            f'<|{courier}|>')
        # new_courier = Couriers()
        # new_courier.courier_id = courier_id
        # TODO: Courier type

    return '<h1>WORKING</h1>'  # jsonify(['Okay, here is goes your couriers'])


# 2) PATCH /couriers/$courier_id
@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
def patch_couriers(courier_id):
    return jsonify(['Okay, PATCH `EM ALL', courier_id])


# 3) POST /orders
@app.route('/orders', methods=['POST'])
def set_orders():
    return jsonify(['Okay, new ORDERS is COMING'])


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


def main():
    db_session.global_init_sqlite('db.sqlite')
    app.run()


if __name__ == '__main__':
    main()
