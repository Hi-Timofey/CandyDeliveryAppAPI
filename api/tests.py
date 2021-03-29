from app import app as tested_app
from data import db_session, couriers, transport_type, orders, regions
from cerberus import Validator
import pytest
from random import randint
from datetime import time
import os

v = Validator()
db_file = 'db_for_tests.sqlite'
db_session.global_init_sqlite(db_file)

client = tested_app.test_client()


type_0 = transport_type.TransportTypes(
    type_name='foot',
    type_weight=10,
    type_earn_coefficient=2)
type_1 = transport_type.TransportTypes(
    type_name='bike',
    type_weight=15,
    type_earn_coefficient=5)
type_2 = transport_type.TransportTypes(
    type_name='car',
    type_weight=50,
    type_earn_coefficient=9)


def clear_db():
    os.remove(db_file)


def get_test_db():
    session = db_session.create_session()
    return session


def test_convert_wh_hours_to_time():
    input_data = [
        ['11:00-12:00', '15:34-17:35'],
        ['01:00-23:00']
    ]
    output_data = [
        [[time(11, 00), time(12, 0)], [time(15, 34), time(17, 35)]],
        [[time(1, 0), time(23, 00)]]
    ]
    for i in range(len(input_data)):
        inp = input_data[i]
        out = output_data[i]
        print('For input:', f'"{inp}"', f'with correct: "{out}"')
        answer = couriers.convert_wh_hours_to_time(inp)
        print('Answer is:', f'"{answer}"')
        assert out == answer


def test_convert_wh_hours_to_str():
    input_data = [
        ['11:00-12:00', '15:34-17:35'],
        ['11:36-17:07', '13:34-18:35', '20:23-21:47'],
        ['01:00-23:00']
    ]
    output_data = [
        '["11:00-12:00", "15:34-17:35"]',
        '["11:36-17:07", "13:34-18:35", "20:23-21:47"]',
        '["01:00-23:00"]'
    ]
    for i in range(len(input_data)):
        inp = input_data[i]
        out = output_data[i]
        print('For input:', f'"{inp}"', f'with correct: "{out}"')
        answer = couriers.convert_wh_hours_to_str(inp)
        print('Answer is:', f'"{answer}"')
        assert out == answer


def test_validate_wh_wrong():
    input_bad_data = [
        '', 1, [], [[], []], None, ['', ''], ['ab:00-12:00'], ['01:00-23:a0'],
        ['01:0o-23:00'],
        ['11:80-13:00'],
        ['11:00-13:60'],
        ['11:00-25:60'],
        ['01:00:23:00']
    ]
    for inp in input_bad_data:
        print('For input:', f'"{inp}"')
        answer = couriers.validate_wh(inp)
        print('Answer is:', f'"{answer}"')
        assert not answer

    input_wrong_time_data = [['11:00-12:00', '15:34-15:33'],
                             ['11:36-23:07', '13:04-18:75', '20:23-25:47'],
                             ['11-00:12-39']
                             ]

    for inp in input_wrong_time_data:
        print('For input:', f'"{inp}"')
        answer = couriers.validate_wh(inp)
        print('Answer is:', f'"{answer}"')
        assert not answer


def test_validate_wh_okay():
    input_data = [
        ['11:00-12:00', '15:34-17:35'],
        ['11:36-17:07', '13:34-18:35', '20:23-21:47'],
        ['01:00-23:00']
    ]
    for inp in input_data:
        answer = couriers.validate_wh(inp)
        assert answer


def test_validate_patch_ok():
    session = get_test_db()
    inp_d_ok = [{"regions": [11, 33, 2]},
                {"courier_type": 'foot'},
                {"courier_type": 'bike'},
                {"courier_type": 'car'},
                {"working_hours": ['11:00-12:00', '15:34-17:35']},
                {"courier_type": 'foot',
                 "working_hours": ['11:00-12:00', '15:34-17:35']},
                {"regions": [11, 33, 2],
                 "working_hours": ['11:00-12:00', '15:34-17:35']},
                {"regions": [11, 33, 2],
                 "working_hours": ['11:00-12:00', '15:34-17:35'],
                 "courier_type": 'foot'}]
    for inp in inp_d_ok:
        print('For input:', f'"{inp}"')
        answer = couriers.Couriers.validate_patch(inp, session)
        print('Answer is:', f'"{answer}"')
        assert answer


def test_validate_patch_wrong():
    inp_d_wrong = [{}, [], '', None, 1, 1.5,
                   {"regions": [-11, 33, 2]},
                   {"region": [-11, 33, 2]},
                   {"region": str},
                   {"region": ''},
                   {"region": None},
                   {"courier_type": 1},
                   {"courier_type": 'feot'},
                   {"courier_typ": ['foot']},
                   {"courier_typ": None},
                   {"working_hous": ['11:00-12:00', '15:34-17:35']},
                   {"working_hours": ['11:00-12:00', '19:34-17:35']},
                   {"working_hours": ['11:0012:00', '19:34-17:35']},
                   {"working_hours": ['11:00-12:00', '19:34-a7:35']},
                   {"working_hours": ['11:00-11:00', '15:34-17:35']},
                   {"working_hours": ['10:00-11:00', '00:00-00:60']},
                   {"working_hours": ['10:00-11:00', '0:00-00:60']},
                   {"working_hours": ['10:00-11:0', '00:00-00:60']},
                   {"working_hours": [None, '00:00-00:60']},
                   {"working_hours": ['21:00-12:00', '15:34-17:35']}
                   ]
    for inp in inp_d_wrong:
        print('For input:', f'"{inp}"')
        answer = couriers.Couriers.validate_patch(inp)
        print('Answer is:', f'"{answer}"')
        assert not answer


def test_could_he_take():
    c0 = couriers.Couriers(courier_type=type_1,
                           working_hours=[],
                           regions=[])
    inp_d_ok = []
    for inp in inp_d_ok:
        print('For input:', f'"{inp}"')
        answer = couriers.Couriers.validate_patch(inp)
        print('Answer is:', f'"{answer}"')
        assert answer


def test_post_couriers_wrong():
    session = get_test_db()
    data = [
        {'data': [{
                    "courier_id": 400,
                    "courier_type": "bike",
                    "regions": [-22],
                    "working_hours": ["09:00-18:00"]
                 }]},
        {'data': [{
                    "courier_id": 400,
                    "courier_type": "biki",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                 }]},
        {'data': [{
                    "courier_id": 400,
                    "courier_type": "bike",
                    "regions": "22",
                    "working_hours": ["09:00-18:00"]
                 }]},
        {'data': [{
                    "courier_id": 400,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["19:00-18:00"]
                 }]},
        {'data': [{
                    "courier_id": 400,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": [""]
                 }]},
    ]
    data_r = {
        "validation_error": {
            "couriers": [{"id": 400}]
            }
        }

    for inp in data:

        res = client.post('/couriers', json=inp)
        assert res.status_code == 400
        assert res.get_json() == data_r


def test_post_couriers():
    session = get_test_db()
    data = [{
        'data': [
                 {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                 },
                 {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                 }
               ]
    }]
    data_r = {
        "couriers": [{"id": 1}, {"id": 2}]
    }

    for inp in data:

        res = client.post('/couriers', json=inp)
        assert res.status_code == 201
        assert res.get_json() == data_r


def test_post_orders():
    session = get_test_db()

    data = [{
        "data": [
            {
                "order_id": 11,
                "weight": 1.11,
                "region": 11,
                "delivery_hours": [
                    "00:11-11:11"
                    ]
                },
            {
                "order_id": 22,
                "weight": 12,
                "region": 22,
                "delivery_hours": [
                    "02:00-12:22"
                    ]
                },
            {
                "order_id": 33,
                "weight": 41,
                "region": 33,
                "delivery_hours": [
                    "03:00-13:00",
                    "16:00-23:30"
                    ]
                }
            ]
        }, {
        "data": [
            {
                "order_id": 1,
                "weight": 1.11,
                "region": 1,
                "delivery_hours": [
                    "00:11-11:11"
                    ]
                },
            {
                "order_id": 2,
                "weight": 12,
                "region": 2,
                "delivery_hours": [
                    "02:00-12:22"
                    ]
                },
            {
                "order_id": 3,
                "weight": 41,
                "region": 3,
                "delivery_hours": [
                    "03:00-13:00",
                    "16:00-23:30"
                    ]
                }
            ]
        }]
    data_r = [{
        "orders": [{"id": 11}, {"id": 22}, {"id": 33}, ]
    }, {
        "orders": [{"id": 1}, {"id": 2}, {"id": 3}, ]
    }]

    for i in range(len(data)):

        inp = data[i]
        out = data_r[i]

        res = client.post('/orders', json=inp)

        assert res.status_code == 201
        json = res.get_json()

        assert json == out


def test_post_orders_wrong():
    session = get_test_db()

    data = [{
            "data": [
                {
                    "order_id": 1001,
                    "weight": 1.11,
                    "region": -5,
                    "delivery_hours": [
                        "00:11-11:11"
                    ]
                }
            ]
            }, {
            "data": [
                {
                    "order_id": 1001,
                    "weight": 1.11,
                    "region": "11",
                    "delivery_hours": [
                        "00:11-11:11"
                    ]
                }
            ]
            },

            {
            "data": [
                {
                    "order_id": 1001,
                    "weight": 1.11,
                    "region": 11,
                    "delivery_hours": [
                        "12:11-11:11"
                    ]
                }
            ]
            },
            {
        "data": [
            {
                "order_id": 1001,
                "weight": 34,
                "region": 2000,
                "delivery_hours": [
                    "12:11-11:11"
                    ]
                }
            ]
        }
            ]
    data_r = {
        "validation_error": {
            "orders": [{"id": 1001}]
            }
        }

    for i in range(len(data)):

        inp = data[i]

        res = client.post('/orders', json=inp)

        print(f'TESTING DATA[{i}]:', end='\t')

        assert res.status_code == 400

        print(f'status {res.status_code}', end='\t')

        json = res.get_json()
        assert json == data_r

        print(f'ALL OK')


def test_patch_couriers():
    session = get_test_db()
    data = [
        (1, {"courier_type": "foot",
             "regions": [1, 12, 22],
             "working_hours": ["11:35-14:05", "09:00-11:00"]
             }),
        (2, {"courier_type": "bike",
             "regions": [22],
             "working_hours": ["09:00-18:00"]
             }),
        (1, {"courier_type": "car",
             "regions": [212],
             }),
        (2, {"working_hours": ["04:00-10:00"]
             }),
    ]
    data_r = [
        {"courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]},
        {"courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]},
        {"courier_id": 1,
            "courier_type": "car",
            "regions": [212],
            "working_hours": ["11:35-14:05", "09:00-11:00"]},
        {"courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["04:00-10:00"]}
    ]

    for i in range(len(data)):
        id_, inp = data[i]
        res = client.patch(f'/couriers/{id_}', json=inp)
        assert res.status_code == 200
        assert res.get_json() == data_r[i]


def test_patch_couriers_wrong():
    data = [
        (1, {"courier_type": "feot",
             "regions": [1, 12, 22],
             "working_hours": ["11:35-14:05", "09:00-11:00"]
             }),
        (2, {"courier_type": "bike",
             "regions": [-22],
             "working_hours": ["09:00-18:00"]
             }),
        (1, {"courier_type": "car",
             "regions": 212,
             }),
        (2, {"working_hours": ["14:00-10:00"]
             }),
        (2, {"woking_hours": ["14:00-10:00"]
             })
    ]

    for i in range(len(data)):
        id_, inp = data[i]
        print(f'TESTING DATA[{i}]: {inp}', end='\t')
        res = client.patch(f'/couriers/{id_}', json=inp)
        assert res.status_code == 400


def test_assigment():
    session = get_test_db()
    cour_id = randint(2058, 3000)
    # adding courier for delivery
    cours = {'data': [
                 {
                    "courier_id": cour_id,
                    "courier_type": "bike",
                    "regions": [2058, 3000],
                    "working_hours": ["10:00-14:00", "16:00-19:00"]
                 }
               ]
             }
    cour_req = client.post('/couriers', json=cours)
    assert cour_req.status_code == 201

    # adding orders ( odd id - okay order; not odd - wrong )
    ords = {
        "data": [
            {
                "order_id": 2500,
                "weight": 11.11,
                "region": 2058,
                "delivery_hours": [
                    "10:11-11:11", "16:55-17:10"
                    ]
                },
            {
                "order_id": 2502,
                "weight": 12,
                "region": 3000,
                "delivery_hours": [
                    "13:45-14:22"
                    ]
                },
            {"order_id": 2501,
                "weight": 10,
                "region": 2058,
                "delivery_hours": [
                    "19:00-23:30",  # wrong time
                    "09:00-10:00"
                    ]},
            {"order_id": 2503,
                "weight": 10,
                "region": 4,  # wrong region
                "delivery_hours": [
                    "16:00-23:30"
                    ]},
            {"order_id": 2059,
                "weight": 41,  # wrong weight
                "region": 2058,
                "delivery_hours": [
                    "03:00-13:00",
                    "16:00-23:30"
                    ]}
            ]
        }

    valid_orders = [{'id': 2500}, {'id': 2502}]

    ords_req = client.post('/orders', json=ords)
    assert ords_req.status_code == 201

    res = client.post(f'/orders/assign', json={'courier_id': cour_id})
    assert res.status_code == 200

    assert res.get_json()['orders'] == valid_orders


def test_clear_testing_database():
    clear_db()
