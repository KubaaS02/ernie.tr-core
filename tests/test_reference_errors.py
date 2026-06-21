import pytest
from tests import BusinessError, ProjectInUseError


class TestProjectInUseError:
    """Testy związane z grupą błędów referencji projektów"""

    def test_ProjectInUseError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-REF-01"""
        assert ProjectInUseError.error_id == "ERR-REF-01"

    def test_ProjectInUseError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = project_in_use"""
        assert ProjectInUseError.error_code == "project_in_use"

    def test_ProjectInUseError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 409"""
        assert ProjectInUseError.http_status == 409

    def test_ProjectInUseError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy projekt jest używany przez innego taska"""
        details = {"project_id": "project1", "active_tasks": 5}
        error = ProjectInUseError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, ProjectInUseError)

        with pytest.raises(ProjectInUseError):
            raise ProjectInUseError(
                details=details)

    def test_ProjectInUseError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"project_id": "project1", "active_tasks": 5}
        error = ProjectInUseError(details=details)
        assert error.details == details

    def test_ProjectInUseError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = ProjectInUseError(
            details={"project_id": "project1", "active_tasks": 5})
        assert error.message == ProjectInUseError.default_message

    def test_ProjectInUseError_to_json_value_on_minus(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy projekt jest używany przez innego taska"""
        details = {"project_id": "project1", "active_tasks": 5}
        error = ProjectInUseError(details=details)
        result = error.to_json()
        assert result["error_code"] == "project_in_use"
        assert result["http_status"] == 409
        assert result["message"] == ProjectInUseError.default_message
        assert result["details"] == details
