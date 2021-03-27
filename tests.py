from app import app as tested_app
from data import db_session, couriers, transport_type
from cerberus import Validator
import pytest
from datetime import time
import os

v = Validator()
db_file = 'db_for_tests.sqlite'
db_session.global_init_sqlite(db_file)


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
    print('-'*10, session.bind.url.database, 'IS DB', '-'*10)
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


def test_validate_regions_wrong():
    input_bad_data = [
        '', 1, [-1], [[], []], None, [4, True, 12], [1, ''], [14, 4, -5],
        [123, 'a', 213],
        [1, 2, 3, 4, 4, 4]
    ]
    for inp in input_bad_data:
        print('For input:', f'"{inp}"')
        answer = couriers.Couriers.validate_regions(inp)
        print('Answer is:', f'"{answer}"')
        assert not answer


def test_validate_regions_okay():
    input_okay_data = [[1, 2, 3], [12, 23, 123], [35, 30]]
    for inp in input_okay_data:
        answer = couriers.Couriers.validate_regions(inp)
        assert answer


def test_validate_wh_wrong():
    input_bad_data = [
        '', 1, [], [[], []], None, ['', ''], ['ab:00-12:00'], ['01:00-23:a0'],
        ['01:0o-23:00'],
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
    session = get_test_db()
    inp_d_wrong = [{}, [], '', None, 1, 1.5,
                   {"regions": [-11, 33, 2]},
                   {"region": [-11, 33, 2]},
                   {"region": str},
                   {"region": ''},
                   {"region": None},
                   {"courier_type": 1},
                   {"courier_type": 'feet'},
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
        answer = couriers.Couriers.validate_patch(inp, session)
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


def test_post_couriers():
    session = get_test_db()
    client = tested_app.test_client()
    data = {
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
    }
    data_r = {
        "couriers": [{"id": 1}, {"id": 2}]
    }

    res = client.post('/couriers', json=data)
    assert res.status_code == 201

    # json = res.get_json()
    # assert json['couriers']
    # assert isinstance(json['couriers'], list)
    # assert len(json['couriers']) == 2

    # assert json['couriers'][0]['id'] == data_r['couriers'][0]['id']
    # assert json['couriers'][1]['id'] == data_r['couriers'][1]['id']
    # assert isinstance(
    #     json['couriers'][0]['id'], type(
    #         data['data'][0]['courier_id']))
    # assert isinstance(
    #     json['couriers'][1]['id'], type(
    #         data['data'][1]['courier_id']))

    # assert isinstance(
    #     json['couriers'][0]['id'], type(
    #         data_r['couriers'][0]['id']))
    # assert isinstance(
    #     json['couriers'][1]['id'], type(
    #         data_r['couriers'][1]['id']))

    # res = client.post('/couriers', json=data)
    # assert res.status_code == 400
    # assert res.get_json()['validation_error']
    # json = res.get_json()['validation_error']

    # assert json['couriers']
    # assert isinstance(json['couriers'], list)
    # assert len(json['couriers']) == 2

    # assert json['couriers'][0]['id'] == 1
    # assert json['couriers'][1]['id'] == 2
    # assert isinstance(
    #     json['couriers'][0]['id'], type(
    #         data['data'][0]['courier_id']))
    # assert isinstance(
    #     json['couriers'][1]['id'], type(
    #         data['data'][1]['courier_id']))

    # assert isinstance(
    #     json['couriers'][0]['id'], type(
    #         data_r['couriers'][0]['id']))
    # assert isinstance(
    #     json['couriers'][1]['id'], type(
    #         data_r['couriers'][1]['id']))


def test_post_orders():

    session = get_test_db()

    client = tested_app.test_client()
    data = {'data':
            [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 1,
                    "delivery_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "order_id": 2,
                    "weight": 43,
                    "region": 2,
                    "delivery_hours": ["09:00-18:00"]
                }]

            }
    data_r = {
        "orders": [{"id": 1}, {"id": 2}]
    }

    res = client.post('/orders', json=data)

    assert res.status_code == 201

    # json = res.get_json()
    # assert json['orders']
    # assert isinstance(json['orders'], list)
    # assert len(json['orders']) == 2

    # assert json['orders'][0]['id'] == data_r['orders'][0]['id']
    # assert json['orders'][1]['id'] == data_r['orders'][1]['id']

    # assert isinstance(
    #     json['orders'][0]['id'], type(
    #         data_r['orders'][0]['id']))
    # assert isinstance(
    #     json['orders'][1]['id'], type(
    #         data_r['orders'][1]['id']))

    # res = client.post('/orders', json=data)
    # assert res.status_code == 400
    # assert res.get_json()['validation_error']
    # json = res.get_json()['validation_error']

    # assert json['orders']
    # assert isinstance(json['orders'], list)
    # assert len(json['orders']) == 2

    # assert json['orders'][0]['id'] == 1
    # assert json['orders'][1]['id'] == 2
    # assert isinstance(
    #     json['orders'][0]['id'], type(
    #         data['data'][0]['order_id']))
    # assert isinstance(
    #     json['orders'][1]['id'], type(
    #         data['data'][1]['order_id']))

    # assert isinstance(
    #     json['orders'][0]['id'], type(
    #         data_r['orders'][0]['id']))
    # assert isinstance(
    #     json['orders'][1]['id'], type(
    #         data_r['orders'][1]['id']))


def test_clear_testing_database():
    clear_db()
