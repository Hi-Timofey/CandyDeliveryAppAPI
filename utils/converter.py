from datetime import time
import json


def convert_wh_hours_to_time(working_hours):
    answer = []
    for wh in working_hours:
        period = wh.split('-')
        time_from = time.fromisoformat(period[0])
        time_to = time.fromisoformat(period[1])
        answer.append([time_from, time_to])
    return answer


def convert_wh_hours_to_str(working_hours):
    answer = json.dumps(working_hours)
    return answer
