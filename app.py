from flask import Flask
from flask import jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import os
from pprint import pprint

from data import db_session
from data.couriers import Couriers#, CouriersSchema


app = Flask(__name__)

client = app.test_client()

app.config['SECRET_KEY'] = os.getenv('KEY')


# 1) POST /couriers
@app.route('/couriers', methods=['POST'])
def get_couriers():
    data = request.get_json()
    couriers_list = data['data']

    for courier in couriers_list:
        courier_id = courier['courier_id']
        courier_type = courier['courier_type']
        regions = courier['regions']
        working_hours = courier['working_hours']

        db_sess = db_session.create_session()
        new_courier = Couriers()
        new_courier.courier_id = courier_id
        # TODO: Courier type


    return jsonify(['Okay, here is goes your couriers'])


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
