from models.task import Task
from models.day import day
from models.task import Task
from models.project import project
from models. change_log import ChangeLogEntry
from core.salary.task_salary import (
    get_approx_cost_pln,
    get_approx_cost_from_pln_to_euro,
    get_actual_cost_pln,
    get_actual_cost_euro_from_pln,
    get_actual_approx_cost_diff,
    get_diff_day, get_diff_month,
    get_approx_day_cost,
    get_actual_day_cost,
    get_approx_month_cost,
    get_actual_month_cost,
    get_avg_rate_pln_per_h,
    get_avg_rate_eur_per_h)
from exceptions.handler_error import BusinessError
from core.time.task_duration import (
    get_task_time_duration,
    get_tasks_time_one_day,
    get_tasks_time_one_month,)
from exceptions.time_errors import InvalidTaskTimeRangeError, TaskOverlapError
from exceptions.finance_errors import InvalidExchangeRateError, InvalidHourlyRateError
from exceptions.authorization_errors import TaskLockedError
from exceptions.reference_errors import ProjectInUseError, EntityNotFoundError
from exceptions.data_errors import MissingCalculationDataError
from exceptions.integration_errors import NbpApiUnavailableError
from exceptions.generic_errors import GenericSystemError
from exceptions.data_errors import IncompleteChangeLogEntryError
from helper.enums import ChangeLogActions
from helper.text import is_blank

# Puste wartości do testów
BLANK_VALUES: list[str] = [
    "",
    " ",
    "   ",
    "\t",
    "\n",
    "\r\n",
    "\u00a0",
    "\u3000",
    "\u200b",
    " \t\u200b ",
]
BLANK_IDS: list[str] = [
    "empty",
    "space",
    "three_spaces",
    "tab",
    "newline",
    "crlf",
    "nbsp",
    "ideographic_space",
    "zero_width_space",
    "mixed",
]

# Białe znaki
WHITESPACE_VALUES: list[str] = BLANK_VALUES[1:]
WHITESPACE_IDS: list[str] = BLANK_IDS[1:]
