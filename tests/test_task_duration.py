import pytest
from datetime import datetime
from tests import get_task_time_duration, get_tasks_time_one_day, get_tasks_time_one_month
from tests import Task
from typing import Tuple
class TestCalculateTaskDuration:
    """Testy obliczania czasu trwania tasku"""
    
    # ============ TESTY PODSTAWOWE ============
    
    def test_regular_task_64_minutes(self) -> None:
        """Test zwykłego tasku - 64 minuty"""
        result: int = get_task_time_duration(
            "2025-11-01 19:44",
            "2025-11-01 20:48"
        )
        assert result == 64
    
    def test_task_one_hour(self) -> None:
        """Test tasku trwającego dokładnie 1 godzinę"""
        result: int = get_task_time_duration(
            "2025-11-01 10:00",
            "2025-11-01 11:00"
        )
        assert result == 60
    
    def test_task_half_hour(self) -> None:
        """Test tasku trwającego 30 minut"""
        result: int = get_task_time_duration(
            "2025-11-01 10:00",
            "2025-11-01 10:30"
        )
        assert result == 30
    
    # ============ TESTY Z SEKUNDAMI ============
    
    def test_task_with_seconds_45_seconds(self) -> None:
        """Test tasku z sekundami - 45 sekund (zaokrągli do 1 minuty)"""
        result: int = get_task_time_duration(
            "2025-11-01 09:00:00",
            "2025-11-01 09:00:45"
        )
        assert result == 1
    
    def test_task_with_seconds_90_seconds(self) -> None:
        """Test tasku z sekundami - 90 sekund (zaokrągli do 2 minut)"""
        result: int = get_task_time_duration(
            "2025-11-01 09:00:00",
            "2025-11-01 09:01:30"
        )
        assert result == 2
    
    def test_task_with_seconds_and_minutes(self) -> None:
        """Test tasku z minutami i sekundami"""
        result: int = get_task_time_duration(
            "2025-11-01 10:00:00",
            "2025-11-01 10:05:30"
        )
        assert result == 6  # 5.5 minut zaokrąglone w górę
    
    # ============ TESTY PRZEJŚCIA PRZEZ PÓŁNOC ============
    
    def test_task_crossing_midnight_45_minutes(self) -> None:
        """Test tasku przechodzącego przez północ - 45 minut"""
        result: int = get_task_time_duration(
            "2025-11-01 23:30",
            "2025-11-02 00:15"
        )
        assert result == 45
    
    def test_task_crossing_midnight_short(self) -> None:
        """Test krótkiego tasku przez północ"""
        result: int = get_task_time_duration(
            "2025-11-01 23:55",
            "2025-11-02 00:05"
        )
        assert result == 10
    
    def test_task_crossing_midnight_long(self) -> None:
        """Test długiego tasku przez północ - 2 godziny"""
        result: int = get_task_time_duration(
            "2025-11-01 22:30",
            "2025-11-02 00:30"
        )
        assert result == 120
    
    # ============ EDGE CASES TESTS ============
    
    def test_task_same_start_and_stop_minimum_one_minute(self) -> None:
        """Test gdy start = stop (minimum 1 minuta)"""
        result: int = get_task_time_duration(
            "2025-11-01 10:00",
            "2025-11-01 10:00"
        )
        assert result == 1
    
    def test_task_very_short_30_seconds(self) -> None:
        """Test bardzo krótkiego tasku - 30 sekund (min 1 minuta)"""
        result: int = get_task_time_duration(
            "2025-11-01 10:00:00",
            "2025-11-01 10:00:30"
        )
        assert result == 1
    
    def test_task_full_day(self) -> None:
        """Test tasku trwającego pełny dzień"""
        result: int = get_task_time_duration(
            "2025-11-01 00:00",
            "2025-11-02 00:00"
        )
        assert result == 1440  # 24 godziny
    
    # ============ TESTY OBSŁUGI FORMATÓW ============
    
    def test_with_datetime_objects(self) -> None:
        """Test z obiektami datetime"""
        start = datetime(2025, 11, 1, 19, 44)
        stop = datetime(2025, 11, 1, 20, 48)
        result: int = get_task_time_duration(start, stop)
        assert result == 64
    
    def test_mixed_string_and_datetime(self) -> None:
        """Test ze stringiem i datetime'em"""
        result: int = get_task_time_duration(
            "2025-11-01 19:44",
            datetime(2025, 11, 1, 20, 48)
        )
        assert result == 64
    
    def test_with_seconds_in_format(self) -> None:
        """Test pełnego formatu ze sekundami"""
        result: int = get_task_time_duration(
            "2025-11-01 09:00:00",
            "2025-11-01 09:00:45"
        )
        assert result == 1
    
    # ============ TESTY BŁĘDÓW ============
    
    def test_start_after_stop_raises_error(self) -> None:
        """Test gdy task_start > task_stop (powinien rzucić błąd)"""
        with pytest.raises(ValueError, match="task_start"):
            get_task_time_duration(
                "2025-11-01 20:48",
                "2025-11-01 19:44"
            )
    
    def test_invalid_format_raises_error(self) -> None:
        """Test nieprawidłowego formatu"""
        with pytest.raises(ValueError):
            get_task_time_duration(
                "01-11-2025 19:44",  # Zły format
                "2025-11-01 20:48"
            )
    
    def test_invalid_type_raises_error(self) -> None:
        """Test nieprawidłowego typu"""
        with pytest.raises(TypeError):
            get_task_time_duration(
                12345,  # Liczba zamiast str/datetime
                "2025-11-01 20:48"
            )
    
    # ============ TESTY Z RZECZYWISTYMI SCENARIUSZAMI ============
    
    def test_fiverr_typical_session(self) -> None:
        """Test typowej sesji pracy (fiverr scenario)"""
        result: int = get_task_time_duration(
            "2025-11-15 14:30",
            "2025-11-15 16:15"
        )
        assert result == 105  # 1h 45min
    
    def test_night_shift_task(self) -> None:
        """Test nocnej zmiany"""
        result: int = get_task_time_duration(
            "2025-11-15 22:00",
            "2025-11-16 06:00"
        )
        assert result == 480  # 8 godzin
    
    def test_tasks_time_one_day(self):
        tasks = [Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 10, 4)), Task(task_id="2", task_start=datetime(2025, 11, 1, 14, 30), task_stop=datetime(2025, 11, 1, 16, 5))]
        total_min, total_hm = get_tasks_time_one_day(tasks, datetime(2025, 11, 1))
        assert total_min == 159
        assert total_hm == '02:39'
    
    def test_tasks_time_one_month(self):
        tasks = [
            Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 10, 4)),
            Task(task_id="2", task_start=datetime(2025, 11, 1, 14, 30), task_stop=datetime(2025, 11, 1, 16, 5)),
            Task(task_id="3", task_start=datetime(2025, 11, 2, 10, 0),  task_stop=datetime(2025, 11, 2, 11, 0))
        ]
        total_min, total_hm = get_tasks_time_one_month(tasks, datetime(2025, 11, 1))
        assert total_min == 219
        assert total_hm == '03:39'
        
    def test_task_time_one_day_correct_month(self):
        tasks = [
            Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 10, 4)),
            Task(task_id="2", task_start=datetime(2025, 11, 1, 14, 30), task_stop=datetime(2025, 11, 1, 16, 5)),
            Task(task_id="3", task_start=datetime(2025, 11, 2, 10, 0),  task_stop=datetime(2025, 11, 2, 11, 0)),
            Task(task_id="4", task_start=datetime(2025, 12, 2, 10, 0),  task_stop=datetime(2025, 12, 2, 11, 0))
        ]
        total_min,total_hm = get_tasks_time_one_month(tasks, datetime(2025, 11, 1))
        assert total_min == 219
        assert total_hm == '03:39'