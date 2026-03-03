from models.task import Task

def approx_cost_pln(task:Task, rate_pln_per_h:float) -> float:
    rate = task.rate_pln_per_h if task.rate_pln_per_h is not None else rate_pln_per_h
    
    if rate <= 0:
        raise ValueError("Stawka za godzinę musi być większa niż 0")
    
    duration_hours = task.duration_min / 60
    cost_approx_pln_raw = duration_hours * rate
    cost_approx_pln = round(cost_approx_pln_raw, 2)
    return cost_approx_pln

def approx_cost_from_PLN_to_EURO(task:Task, rate_euro_pln:float) -> float:
    if rate_euro_pln <0 :
        raise ValueError("Kurs musi być większy niż 0")
    
    cost_approx_eur_raw = task.cost_approx_pln / rate_euro_pln
    cost_approx_eur = round(cost_approx_eur_raw, 2)
    return cost_approx_eur