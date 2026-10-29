import pytest
from datetime import datetime, timezone
from tests import (
    ChangeLogEntry,
    IncompleteChangeLogEntryError,
    ChangeLogActions,
    BLANK_IDS,
    BLANK_VALUES,
    WHITESPACE_IDS,
    WHITESPACE_VALUES,
)

TASK_ID = "7f3a1c2e-0b4d-4a91-9c88-1e2f3a4b5c6d"
USER_ID = "1a2b3c4d-5e6f-4071-8293-a4b5c6d7e8f9"
TIMESTAMP = datetime(2026, 9, 22, 14, 30)


class TestChangeLogEntryValid:
    """Testy poprawnego tworzenia wpisów w historii zmian"""

    def test_change_log_entry_unlock_without_reason(self) -> None:
        """Sprawdzenie, czy wpis unlock bez uzasadnienia zostanie utworzony"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.unlock)
        assert entry.action is ChangeLogActions.unlock
        assert entry.field is None
        assert entry.old_value is None
        assert entry.new_value is None
        assert entry.reason is None

    def test_change_log_entry_unlock_with_reason(self) -> None:
        """Sprawdzenie, czy wpis unlock przechowuje uzasadnienie"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.unlock,
                               reason="Klient skorygował kwotę wypłaty")
        assert entry.reason == "Klient skorygował kwotę wypłaty"

    def test_change_log_entry_delete(self) -> None:
        """Sprawdzenie, czy wpis delete zostanie utworzony bez pól zmiany i uzasadnienia"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.delete)
        assert entry.action is ChangeLogActions.delete
        assert entry.field is None
        assert entry.old_value is None
        assert entry.new_value is None
        assert entry.reason is None

    def test_change_log_entry_field_change_complete(self) -> None:
        """Sprawdzenie, czy kompletny wpis field_change zostanie utworzony"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.field_change,
                               field="cost_actual_pln",
                               old_value="450.00",
                               new_value="480.00")
        assert entry.field == "cost_actual_pln"
        assert entry.old_value == "450.00"
        assert entry.new_value == "480.00"

    def test_change_log_entry_stores_base_data(self) -> None:
        """Sprawdzenie, czy wpis przechowuje task_id, user_id i timestamp"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.unlock)
        assert entry.task_id == TASK_ID
        assert entry.user_id == USER_ID
        assert entry.timestamp == TIMESTAMP


class TestChangeLogEntryTypes:
    """Testy typów pól zgodnie z 4.1.0.2"""

    def test_invalid_action_raises_value_error(self) -> None:
        """Sprawdzenie, czy akcja spoza enuma jest odrzucana"""
        with pytest.raises(ValueError):
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "invalid_action") # type: ignore[arg-type]

    def test_string_action_is_normalized_to_enum(self) -> None:
        """Sprawdzenie, czy action podany jako str. zamienia się na enum"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, "unlock")  # type: ignore[arg-type]
        assert entry.action is ChangeLogActions.unlock

    def test_string_timestamp_raises_type_error(self) -> None:
        """Sprawdzenie, czy timestamp inny niż datetime jest odrzucany"""
        with pytest.raises(TypeError, match="timestamp"):
            ChangeLogEntry(TASK_ID, USER_ID, "2026-09-22 14:30",  # type: ignore[arg-type]
                           ChangeLogActions.unlock)

    @pytest.mark.parametrize(
        ("kwargs", "bad_field"),
        [
            ({"field": 1, "old_value": "450.00", "new_value": "480.00"}, "field"),
            ({"field": "cost_actual_pln", "old_value": 450.0, "new_value": "480.00"}, "old_value"),
            ({"field": "cost_actual_pln", "old_value": "450.00", "new_value": 480.0}, "new_value"),
        ]
    )
    def test_non_string_change_field_raises_type_error(
            self,
            kwargs: dict[str, object],
            bad_field: str,
    ) -> None:
        """Sprawdzenie, czy wartość inna niż str. w polach zmiany jest odrzucana"""
        with pytest.raises(TypeError, match=bad_field):
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP,
                           ChangeLogActions.field_change, **kwargs)  # type: ignore[arg-type]


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
    def test_change_log_entry_field_change_missing_one_field(
            self,
            kwargs: dict[str, str],
            expected_missing: list[str],
    ) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy brakuje jednego z pól zmiany"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP,
                           ChangeLogActions.field_change, **kwargs)
        assert exc_info.value.details["missing_fields"] == expected_missing

    def test_change_log_entry_field_change_missing_all(self) -> None:
        """Sprawdzenie, czy details zawiera wszystkie trzy brakujące pola w stałej kolejności"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.field_change)
        assert exc_info.value.details == {
            "task_id": TASK_ID,
            "action": "field_change",
            "missing_fields": ["field", "old_value", "new_value"]
        }


class TestChangeLogEntryEdgeCases:
    """Testy przypadków brzegowych"""

    def test_change_log_entry_empty_old_value_is_valid(self) -> None:
        """Sprawdzenie, czy pusty string w old_value jest traktowany jako wartość, a nie brak"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.field_change,
                               field="comment", old_value="", new_value="Poprawka")
        assert entry.old_value == ""

    def test_change_log_entry_empty_new_value_is_valid(self) -> None:
        """Sprawdzenie, czy wyczyszczenie pola (new_value = "") jest poprawną zmianą"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.field_change,
                               field="comment", old_value="Stary opis", new_value="")
        assert entry.new_value == ""

    def test_change_log_entry_field_change_with_reason(self) -> None:
        """Sprawdzenie, czy reason jest dozwolony również przy field_change"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.field_change,
                               field="cost_actual_pln", old_value="450.00",
                               new_value="480.00", reason="Korekta po wypłacie")
        assert entry.reason == "Korekta po wypłacie"

    def test_change_log_entry_empty_reason_is_valid(self) -> None:
        """Sprawdzenie, czy pusty reason przy unlock nie powoduje błędu"""
        entry = ChangeLogEntry(
            TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.unlock, reason="")
        assert entry.reason == ""

    def test_change_log_entry_same_old_and_new_value(self) -> None:
        """Sprawdzenie obecnego zachowania: zmiana na tę samą wartość jest akceptowana"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.field_change,
                               field="cost_actual_pln", old_value="450.00", new_value="450.00")
        assert entry.old_value == entry.new_value

    def test_change_log_entry_timezone_aware_timestamp(self) -> None:
        """Sprawdzenie, czy timestamp ze strefą czasową UTC jest akceptowany"""
        aware = datetime(2026, 9, 22, 12, 30, tzinfo=timezone.utc)
        entry = ChangeLogEntry(TASK_ID, USER_ID, aware, ChangeLogActions.unlock)
        assert entry.timestamp.tzinfo == timezone.utc

    def test_change_log_entry_equal_entries(self) -> None:
        """Sprawdzenie, czy dwa wpisy z identycznymi danymi są sobie równe"""
        first = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.delete)
        second = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.delete)
        assert first == second

    def test_change_log_entry_repr_does_not_contain_values(self) -> None:
        """Sprawdzenie, czy __repr__ nie ujawnia kwot (zakaz z 4.0.3 dla logów)"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.field_change,
                               field="cost_actual_pln", old_value="450.00", new_value="480.00")
        result = repr(entry)
        assert TASK_ID in result
        assert "field_change" in result
        assert "450.00" not in result
        assert "480.00" not in result

    def test_change_log_entry_repr_does_not_contain_comment_text(self) -> None:
        """Sprawdzenie, czy __repr__ nie ujawnia treści komentarza (zakaz z 4.0.3)"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.field_change,
                               field="comment", old_value="Stary opis klienta",
                               new_value="Nowy opis klienta")
        assert "opis klienta" not in repr(entry)

    def test_change_log_entry_repr_does_not_contain_reason(self) -> None:
        """Sprawdzenie, czy __repr__ nie ujawnia uzasadnienia użytkownika"""
        entry = ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.unlock,
                               reason="Klient skorygował kwotę wypłaty")
        assert "Klient skorygował" not in repr(entry)


def _field_change_entry(
        field: str | None = "cost_actual_pln",
        old_value: str | None = "450.00",
        new_value: str | None = "480.00",
) -> ChangeLogEntry:
    """Tworzy wpis field_change; argumenty nadpisują poprawne wartości domyślne"""
    return ChangeLogEntry(TASK_ID, USER_ID, TIMESTAMP, ChangeLogActions.field_change,
                          field=field, old_value=old_value, new_value=new_value)


class TestChangeLogEntryBlankValues:
    """Testy pustych wartości i białych znaków w polach zmiany"""

    @pytest.mark.parametrize("blank", BLANK_VALUES, ids=BLANK_IDS)
    def test_change_log_entry_blank_field_raises_error(self, blank: str) -> None:
        """Sprawdzenie, czy pusta nazwa pola lub same białe znaki są odrzucane"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            _field_change_entry(field=blank)
        assert exc_info.value.details["missing_fields"] == ["field"]

    @pytest.mark.parametrize("blank", WHITESPACE_VALUES, ids=WHITESPACE_IDS)
    def test_change_log_entry_whitespace_new_value_for_comment_raises_error(
            self,
            blank: str,
    ) -> None:
        """Sprawdzenie, czy same białe znaki w new_value są odrzucane także dla comment"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            _field_change_entry(field="comment", old_value="Projekt 1", new_value=blank)
        assert exc_info.value.details["missing_fields"] == ["new_value"]

    def test_change_log_entry_empty_new_value_for_other_field_raises_error(self) -> None:
        """Sprawdzenie, czy new_value = "" jest odrzucane dla pola spoza CLEARABLE_FIELDS"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            _field_change_entry(field="cost_actual_pln", new_value="")
        assert exc_info.value.details["missing_fields"] == ["new_value"]

    def test_change_log_entry_blank_field_and_new_value(self) -> None:
        """Sprawdzenie, czy oba puste pola są zgłaszane w stałej kolejności"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            _field_change_entry(field=" ", new_value="")
        assert exc_info.value.details["missing_fields"] == ["field", "new_value"]

    def test_change_log_entry_none_field_and_whitespace_new_value(self) -> None:
        """Sprawdzenie, czy None i same białe znaki trafiają do jednej listy missing_fields"""
        with pytest.raises(IncompleteChangeLogEntryError) as exc_info:
            _field_change_entry(field=None, new_value="   ")
        assert exc_info.value.details["missing_fields"] == ["field", "new_value"]

    @pytest.mark.parametrize("blank", BLANK_VALUES, ids=BLANK_IDS)
    def test_change_log_entry_blank_old_value_is_valid(self, blank: str) -> None:
        """Sprawdzenie, czy pusty old_value lub same białe znaki są akceptowane (stan z przeszłości)"""
        entry = _field_change_entry(field="comment", old_value=blank, new_value="Projekt 1")
        assert entry.old_value == blank

    def test_change_log_entry_new_value_is_stored_unchanged(self) -> None:
        """Sprawdzenie, czy model nie obcina białych znaków wokół treści"""
        entry = _field_change_entry(field="comment", old_value="", new_value="  Nowy opis ")
        assert entry.new_value == "  Nowy opis "
