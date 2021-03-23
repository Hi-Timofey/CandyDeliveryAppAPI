from app import client
import pytest
import utils


def test_validate_wh_wrong():
    input_bad_data = [
        '', 1, [], [[], []], None, ['', ''], ['ab:00-12:00'], ['01:00-23:a0'],
        ['01:0o-23:00'],
        ['01:00:23:00']
    ]
    for inp in input_bad_data:
        print('For input:', f'"{inp}"')
        answer = utils.validation.validate_wh(inp)
        print('Answer is:', f'"{answer}"')
        assert not answer

    input_wrong_time_data = [['11:00-12:00', '15:34-15:33'],
                             ['11:36-23:07', '13:04-18:75', '20:23-25:47'],
                             ['11-00:12-39']
                             ]

    for inp in input_wrong_time_data:
        print('For input:', f'"{inp}"')
        answer = utils.validation.validate_wh(inp)
        print('Answer is:', f'"{answer}"')
        assert not answer


def test_validate_wh_okay():
    input_data = [
        ['11:00-12:00', '15:34-17:35'],
        ['11:36-17:07', '13:34-18:35', '20:23-21:47'],
        ['01:00-23:00']
    ]
    for inp in input_data:
        answer = utils.validation.validate_wh(inp)
        assert answer


# def test_get_couriers():
#     data = {'data':
#             [
#                 {
#                     "courier_id": 1,
#                     "courier_type": "foot",
#                     "regions": [1, 12, 22],
#                     "working_hours": ["11:35-14:05", "09:00-11:00"]
#                 },
#                 {
#                     "courier_id": 2,
#                     "courier_type": "bike",
#                     "regions": [22],
#                     "working_hours": ["09:00-18:00"]
#                 }]

#             }
#     data_r = {
#         "couriers": [{"id": 1}, {"id": 2}]
#         }

#     res = client.post('/couriers', json=data)

#     assert res.status_code == 200

#     json = res.get_json()
#     assert json['couriers']
#     assert isinstance(json['couriers'], list)
#     assert len(json['couriers']) == 2
#     with pytest.raises(BaseException):
#         assert json['couriers'][0]['id']
#         assert json['couriers'][1]['id']
#     assert isinstance(
#         json['couriers'][0]['id'], type(
#             data['data'][0]['courier_id']))
#     assert isinstance(
#         json['couriers'][1]['id'], type(
#             data['data'][1]['courier_id']))
#     assert isinstance(json['couriers'][0]['id'], data['data'][0]['courier_id'])
#     assert isinstance(json['couriers'][1]['id'], data['data'][1]['courier_id'])


if __name__ == '__main__':
    test_validate_wh_okay()
