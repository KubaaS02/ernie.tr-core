import pytest
from datetime import datetime, timezone
from tests import ChangeLogEntry, IncompleteChangeLogEntryError

TASK_ID = "7f3a1c2e-0b4d-4a91-9c88-1e2f3a4b5c6d"
USER_ID = "1a2b3c4d-5e6f-4071-8293-a4b5c6d7e8f9"
TIMESTAMP = datetime(2026, 9, 22, 14, 30)


class TestChangeLogEntryValid:
    """Testy poprawnego tworzenia wpisów w historii zmian"""

    def test_ChangeLogEntry_unlock_without_reason(self) -> None:
        """Sprawdzenie, czy wpis unlock bez uzasadnienia zostanie utworzony"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "unlock")
        assert entry.action == "unlock"
        assert entry.field is None
        assert entry.old_value is None
        assert entry.new_value is None
        assert entry.reason is None

    def test_ChangeLogEntry_unlock_with_reason(self) -> None:
        """Sprawdzenie, czy wpis unlock przechowuje uzasadnienie"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "unlock",
                               reason="Klient skorygował kwotę wypłaty")
        assert entry.reason == "Klient skorygował kwotę wypłaty"

    def test_ChangeLogEntry_delete(self) -> None:
        """Sprawdzenie, czy wpis delete zostanie utworzony bez pól zmiany i uzasadnienia"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "delete")
        assert entry.action == "delete"
        assert entry.field is None
        assert entry.old_value is None
        assert entry.new_value is None
        assert entry.reason is None

    def test_ChangeLogEntry_field_change_complete(self) -> None:
        """Sprawdzenie, czy kompletny wpis field_change zostanie utworzony"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "field_change",
                               field="cost_actual_pln",
                               old_value="450.00",
                               new_value="480.00")
        assert entry.field == "cost_actual_pln"
        assert entry.old_value == "450.00"
        assert entry.new_value == "480.00"

    def test_ChangeLogEntry_stores_base_data(self) -> None:
        """Sprawdzenie, czy wpis przechowuje task_id, user_id i timestamp"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "unlock")
        assert entry.task_id == TASK_ID
        assert entry.user_id == USER_ID
        assert entry.timestamp == TIMESTAMP


class TestChangeLogEntryFieldChangeMissing:
    """Testy wpisów field_change z brakującymi polami"""

    @pytest.mark.parametrize(
        ("kwargs", "expected_missing"),
        [
            ({"old_value": "450.00", "new_value": "480.00"}, ["field"]),
            ({"field": "cost_actual_pln",
             "new_value": "480.00"}, ["old_value"]),
            ({"field": "cost_actual_pln",
             "old_value": "450.00"}, ["new_value"]),
        ]
    )
    def test_ChangeLogEntry_field_change_missing_one_field(
            self,
            kwargs: dict,
            expected_missing: list[str],
    ) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy brakuje jednego z pól zmiany"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP,
                           "field_change", **kwargs)
        assert exc_info.value.details["missing_fields"] == expected_missing

    def test_ChangeLogEntry_field_change_missing_all(self) -> None:
        """Sprawdzenie, czy details zawiera wszystkie trzy brakujące pola w stałej kolejności"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, action="field_change")
        assert exc_info.value.details == {
            "task_id": TASK_ID,
            "action": "field_change",
            "missing_fields": ["field", "old_value", "new_value"]
        }


class TestChangeLogEntryUnexpectedFields:
    """Testy wpisów innych niż field_change, które niosą pola zmiany"""

    def test_ChangeLogEntry_unlock_with_field(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy unlock ma ustawione field"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "unlock",
                           field="cost_actual_pln")
        assert exc_info.value.details["unexpected_fields"] == ["field"]

    def test_ChangeLogEntry_delete_with_old_value(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy delete ma ustawione old_value"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "delete",
                           old_value="450.00")
        assert exc_info.value.details["unexpected_fields"] == ["old_value"]

    def test_ChangeLogEntry_unlock_with_all_change_fields(self) -> None:
        """Sprawdzenie, czy details zawiera wszystkie nadmiarowe pola"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "unlock",
                           field="comment", old_value="", new_value="Nowy")
        assert exc_info.value.details == {
            "task_id": TASK_ID,
            "action": "unlock",
            "unexpected_fields": ["field", "old_value", "new_value"]
        }


class TestChangeLogEntryEdgeCases:
    """Testy przypadków brzegowych"""

    def test_ChangeLogEntry_empty_old_value_is_valid(self) -> None:
        """Sprawdzenie, czy pusty string w old_value jest traktowany jako wartość, a nie brak"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "field_change",
                               field="comment", old_value="", new_value="Poprawka")
        assert entry.old_value == ""

    def test_ChangeLogEntry_empty_new_value_is_valid(self) -> None:
        """Sprawdzenie, czy wyczyszczenie pola (new_value = "") jest poprawną zmianą"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "field_change",
                               field="comment", old_value="Stary opis", new_value="")
        assert entry.new_value == ""

    def test_ChangeLogEntry_empty_string_on_unlock_is_unexpected(self) -> None:
        """Sprawdzenie, czy pusty string w polu zmiany przy unlock też jest odrzucany"""
        with pytest.raises(IncompleteChangeLogEntryError):
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "unlock", old_value="")

    def test_ChangeLogEntry_field_change_with_reason(self) -> None:
        """Sprawdzenie, czy reason jest dozwolony również przy field_change"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "field_change",
                               field="cost_actual_pln", old_value="450.00",
                               new_value="480.00", reason="Korekta po wypłacie")
        assert entry.reason == "Korekta po wypłacie"

    def test_ChangeLogEntry_empty_reason_is_valid(self) -> None:
        """Sprawdzenie, czy pusty reason przy unlock nie powoduje błędu"""
        entry = ChangeLogEntry(
            TASK_ID, USER_ID, TIMESTAMP, "unlock", reason="")
        assert entry.reason == ""

    def test_ChangeLogEntry_same_old_and_new_value(self) -> None:
        """Sprawdzenie obecnego zachowania: zmiana na tę samą wartość jest akceptowana"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "field_change",
                               field="cost_actual_pln", old_value="450.00", new_value="450.00")
        assert entry.old_value == entry.new_value

    def test_ChangeLogEntry_timezone_aware_timestamp(self) -> None:
        """Sprawdzenie, czy timestamp ze strefą czasową UTC jest akceptowany"""
        aware = datetime(2026, 9, 22, 12, 30, tzinfo=timezone.utc)
        entry = ChangeLogEntry(TASK_ID, USER_ID, aware, "unlock")
        assert entry.timestamp.tzinfo == timezone.utc

    def test_ChangeLogEntry_equal_entries(self) -> None:
        """Sprawdzenie, czy dwa wpisy z identycznymi danymi są sobie równe"""
        first = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "delete")
        second = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "delete")
        assert first == second

    def test_ChangeLogEntry_repr_does_not_contain_values(self) -> None:
        """Sprawdzenie, czy __repr__ nie ujawnia kwot (zakaz z 4.0.3 dla logów)"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "field_change",
                               field="cost_actual_pln", old_value="450.00", new_value="480.00")
        result = repr(entry)
        assert TASK_ID in result
        assert "field_change" in result
        assert "450.00" not in result
        assert "480.00" not in result
