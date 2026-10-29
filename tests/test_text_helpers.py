import pytest

from tests import BLANK_IDS, BLANK_VALUES, is_blank


class TestIsBlank:
    """Testy funkcji is_blank"""

    @pytest.mark.parametrize("value", BLANK_VALUES, ids=BLANK_IDS)
    def test_is_blank_returns_true_for_blank_values(self, value: str) -> None:
        """Sprawdzenie, czy pusty tekst i same niewidoczne znaki są uznawane za puste"""
        assert is_blank(value) is True

    @pytest.mark.parametrize(
        "value",
        ["a", " a ", "0", "a\u200b", "Projekt 1"],
        ids=["letter", "letter_with_spaces", "zero", "letter_with_zero_width", "text"],
    )
    def test_is_blank_returns_false_for_values_with_content(self, value: str) -> None:
        """Sprawdzenie, czy tekst z co najmniej jednym widocznym znakiem nie jest pusty"""
        assert is_blank(value) is False
