from app import client
import pytest


def test_get_couriers():
    data = {'data':
            [
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
                }]

            }
    data_r = {
        "couriers": [{"id": 1}, {"id": 2}]
        }

    res = client.post('/couriers', json=data)

    assert res.status_code == 200

    json = res.get_json()
    assert json['couriers']
    assert type(json['couriers']) is list
    assert len(json['couriers']) == 2
    with pytest.raises(BaseException):
        assert json['couriers'][0]['id']
        assert json['couriers'][1]['id']
    assert type(json['couriers'][0]['id']) is type(data['data'][0]['courier_id'])
    assert type(json['couriers'][1]['id']) is type(data['data'][1]['courier_id'])
    assert type(json['couriers'][0]['id']) == data['data'][0]['courier_id']
    assert type(json['couriers'][1]['id']) == data['data'][1]['courier_id']
