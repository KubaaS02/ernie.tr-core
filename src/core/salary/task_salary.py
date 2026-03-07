from models.task import Task

def approx_cost_pln(task:Task, rate_pln_per_h:float) -> float:
    """
    Algorytm oblicza przybliżony koszt tasku w PLN na podstawie czasu pracy i stawki godzinowej.
    
    Args:
        task: Pojedyńczy task (Task)
        rate_pln_per_h: Kwota na godzinę w złotówkach (float)
    
    Returns:
        PRzybliżony koszt tasku w PLN (float)
    
    Raises:
        ValueError: Stawka za godzinę musi być większa niż 0
    
    Examples:
        # Stawka za godzinę jest ustalona przy tworzeniu Taska
        >>> task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ), rate_pln_per_h = 60)
        >>> approx_cost_pln(task, rate_pln_per_h=999)
        (120.0)
        
        # Stawka za godzinę jest nie ustalona przy tworzeniu Taska. Funkcja bierze kwotę na godzinę z argumentu funkcji
        >>> task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ))
        >>> approx_cost_pln(task, rate_pln_per_h=120)
        (240.0)
    """
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