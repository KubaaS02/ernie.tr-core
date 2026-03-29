from dataclasses import dataclass
from typing import List


@dataclass
class Month:
    """
    Model reprezentujący jeden miesiąc (month)

    Attributes:
        month_id: Unikatowy identyfikator miesiąca
        user_id: Identyfikator użytkownika
        year: Rok z którego jest dany miesiąc
        days: Liczba dni, które wchodzą w skład danego miesiąca
        total_duration_month_min: Suma minut w danym miesiącu
        total_duration_month_hm: Suma minut w danym miesiącu (format: str HH:MM)
        cost_approx_month_pln: Przewidywany koszt w danym miesiącu w zł
        cost_approx_month_eur: Przewidywany koszt w danym miesiącu w euro
        cost_actual_month_pln: Rzeczywisty koszt w danym miesiącu w zł
        cost_actual_month_eur: Rzeczywisty koszt w danym miesiącu w euro
        avg_rate_pln_per_h: Średni koszt na godzinę w danym miesiącu w zł
        avg_rate_eur_per_h: Średni koszt na godzinę w danym miesiącu w euro
        num_tasks_total: Liczba zadań w danym miesiącu
        num_tasks_paid: Liczba opłaconych zadań w danym miesiącu
        num_tasks_unpaid: Liczba nie opłaconych zadań w danym miesiącu
    """

    month_id: str
    user_id:  str
    year: int
    days: List
    total_duration_month_min: int
    total_duration_month_hm: str
    cost_approx_month_pln: float
    cost_approx_month_eur: float
    cost_actual_month_pln: float
    cost_actual_month_eur: float
    avg_rate_pln_per_h: float
    avg_rate_eur_per_h: float
    num_tasks_total: int
    num_tasks_paid: int
    num_tasks_unpaid: int

    def correct_days_number(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")

    def unique_month_id(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")

    def mins_sum_have_correct_days_number(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")
