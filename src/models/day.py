from datetime import date
from dataclasses import dataclass
from typing import List


@dataclass
class day:
    """
    Model reprezentujący pojedyńczy dzień (day)

    Attributes:
        day_id: Unikatowy identyfikator dnia
        user_id: Identyfikator użytkownika
        date: Pełna data dnia, zawierająca dodatkowo miesiąc i rok (format: YYYY-MM-DD)
        tasks: Lista tasków w danym dniu
        total_duration_min: Łączny czas trwania zadań w danym dniu (format: int)
        total_duration_hm: Łączny czas trwania zadań w danym dniu (format: str HH:MM)
        cost_approx_day_pln: Przewidywany koszt zadań w danym dniu w zł
        cost_approx_day_eur: Przewidywany koszt zadań w danym dniu w euro
        cost_actual_day_pln: Rzeczywisty koszt zadań w danym dniu w zł
        cost_actual_day_eur: Rzeczywisty koszt zadań w danym dniu w euro
    """

    day_id: str
    user_id: str
    date: date
    tasks: List
    total_duration_min: int
    total_duration_hm: str
    cost_approx_day_pln: float
    cost_approx_day_eur: float
    cost_actual_day_pln: float
    cost_actual_day_eur: float

    def unique_day_id(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")

    def correct_day_in_correct_month(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")

    def check_if_task_duration_is_in_correct_day(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")

    def correct_rate_for_approx_cost(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")

    def correct_rate_for_acctual_cost(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")
