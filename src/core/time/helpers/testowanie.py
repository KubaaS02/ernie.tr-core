from .time import month_days
from datetime import datetime, time, date
from core.time.task_duration import tasks_time_one_day, tasks_time_one_month
from models.task import Task
tasks = [
    # listopad 2025 - dzień 1: 64 + 95 + 30 = 189
    Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 10, 4)),
    Task(task_id="2", task_start=datetime(2025, 11, 1, 14, 30), task_stop=datetime(2025, 11, 1, 16, 5)),
    Task(task_id="3", task_start=datetime(2025, 11, 1, 20, 0),  task_stop=datetime(2025, 11, 1, 20, 30)),

    # listopad 2025 - dzień 2: 240
    Task(task_id="4", task_start=datetime(2025, 11, 2, 8, 0),  task_stop=datetime(2025, 11, 2, 12, 0)),

    # listopad 2025 - dzień 3: 120
    Task(task_id="5", task_start=datetime(2025, 11, 3, 10, 0), task_stop=datetime(2025, 11, 3, 12, 0)),

    # task spoza miesiąca (nie powinien się liczyć)
    Task(task_id="6", task_start=datetime(2025, 10, 31, 23, 0), task_stop=datetime(2025, 10, 31, 23, 30)),
]

mins, hm = tasks_time_one_month(tasks, datetime(2025, 11, 1))

print(mins, hm)

