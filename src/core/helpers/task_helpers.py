from models.task import Task
from exceptions.authorization_errors import TaskLockedError
from exceptions.time_errors import TaskOverlapError


def check_is_locked(task: Task) -> None:
    if task.is_locked:
        raise TaskLockedError(
            details={
                "task_id": task.task_id,
                "is_locked": True,
            }
        )

def check_overlap(t1: Task, t2: Task) -> None:
    if t1.task_start < t2.task_stop and t2.task_start < t2.task_stop:
        raise TaskOverlapError(
            details={"conflicting_task_id": t2.task_id,
                     "range": f"{t2.task_start.strftime('%H:%M')} - {t2.task_stop.strftime('%H:%M')}"
                     }
        )

def tasks_overlap(task1: Task, task2: Task) -> bool:
    return (
        task1.task_start < task2.task_stop
        and task2.task_start < task1.task_stop
    )