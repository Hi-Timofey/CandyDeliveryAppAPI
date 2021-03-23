from datetime import time


def validate_wh(working_hours: list) -> bool:
    if not (isinstance(working_hours, list) and len(working_hours) > 0):
        return False

    for wh in working_hours:
        try:
            period = wh.split('-')
            time_from = time.fromisoformat(period[0])
            time_to = time.fromisoformat(period[1])
        except ValueError as ve:
            return False
        except AttributeError as ae:
            return False
        except BaseException as be:
            raise ValueError(be)

        if not time_from < time_to:
            return False
    return True


def validate_courier_hours(courier_json: dict) -> bool:
    try:
        wh = courier_json['working_hours']
        validate_wh(wh)
        return True
    except BaseException as be:
        raise ValueError('Something went wrong - ' + be)
