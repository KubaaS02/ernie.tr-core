import pytest

from exceptions import InvalidTaskTimeRangeError
from exceptions.authorization_errors import TaskLockedError
from exceptions.data_errors import MissingCalculationDataError
from exceptions.finance_errors import InvalidHourlyRateError
from exceptions.generic_errors import GenericSystemError
from exceptions.integration_errors import NbpApiUnavailableError
from exceptions.reference_errors import ProjectInUseError, EntityNotFoundError
from exceptions.time_errors import TaskOverlapError
from tests import BusinessError, InvalidExchangeRateError


class TestInvalidExchangeRateError:
    """Testy przeprowadzanych operacji związanych z finansami"""

    def test_InvalidExchangeRateError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-FIN-01"""
        assert InvalidExchangeRateError.error_id == "ERR-FIN-01"

    def test_InvalidExchangeRateError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = invalid_exchange_rate"""
        assert InvalidExchangeRateError.error_code == "invalid_exchange_rate"

    def test_InvalidExchangeRateError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 422"""
        assert InvalidExchangeRateError.http_status == 422


    @pytest.mark.parametrize(
        ("error_class", "error_id", "error_code", "http_status"),
        [
            (
                InvalidExchangeRateError,
                "ERR-FIN-01",
                "invalid_exchange_rate",
                422
             ),
            (
                InvalidHourlyRateError,
                "ERR-FIN-02",
                "invalid_hourly_rate",
                422
            )
        ]
    )
    def test_business_error_contract(self, error_class, error_id, error_code, http_status):
        assert error_class.error_id == error_id
        assert error_class.error_code == error_code
        assert error_class.http_status == http_status

    def test_InvalidExchangeRateError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy kurs wymiany waluty będzie < 0"""
        details = {"value": -1}
        error = InvalidExchangeRateError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, InvalidExchangeRateError)
        assert not isinstance(error, ValueError)

        with pytest.raises(InvalidExchangeRateError):
            raise InvalidExchangeRateError(
                details=details)

    def test_InvalidExchangeRateError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"value": 10}
        error = InvalidExchangeRateError(details=details)
        assert error.details == details

    def test_InvalidExchangeRateError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = InvalidExchangeRateError(
            details={"value": -1})
        assert error.message == InvalidExchangeRateError.default_message

    def test_InvalidExchangeRateError_to_json_value_on_minus(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy value = -1"""
        details = {"value": -1}
        error = InvalidExchangeRateError(details=details)
        result = error.to_json()
        assert result["error_code"] == "invalid_exchange_rate"
        assert result["http_status"] == 422
        assert result["message"] == InvalidExchangeRateError.default_message
        assert result["details"] == details

    def test_InvalidExchangeRateError_to_json_value_0(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy value = 0"""
        details = {"value": 0}
        error = InvalidExchangeRateError(details=details)
        result = error.to_json()
        assert result["error_code"] == "invalid_exchange_rate"
        assert result["http_status"] == 422
        assert result["message"] == InvalidExchangeRateError.default_message
        assert result["details"] == details

# błędy InvalidHourlyRateError
    def test_InvalidHourlyRateError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-FIN-02"""
        assert InvalidHourlyRateError.error_id == "ERR-FIN-02"

    def test_InvalidHourlyRateError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = invalid_hourly_rate"""
        assert InvalidHourlyRateError.error_code == "invalid_hourly_rate"

    def test_InvalidHourlyRateError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 422"""
        assert InvalidHourlyRateError.http_status == 422

    def test_InvalidHourlyRateError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy stawka godzinowa będzie < 0"""
        details = {"hourly_rate": -120}
        error = InvalidHourlyRateError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, InvalidHourlyRateError)
        assert not isinstance(error, ValueError)

        with pytest.raises(InvalidHourlyRateError):
            raise InvalidHourlyRateError(
                details=details)

    def test_InvalidHourlyRateError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"hourly_rate": 100}
        error = InvalidHourlyRateError(details=details)
        assert error.details == details

    def test_InvalidHourlyRateError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = InvalidHourlyRateError(
            details={"value": -120})
        assert error.message == InvalidHourlyRateError.default_message

    def test_InvalidHourlyRateError_to_json_value_on_minus(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy hourly_rate = -100"""
        details = {"value": -100}
        error = InvalidHourlyRateError(details=details)
        result = error.to_json()
        assert result["error_code"] == "invalid_hourly_rate"
        assert result["http_status"] == 422
        assert result["message"] == InvalidHourlyRateError.default_message
        assert result["details"] == details

    def test_InvalidHourlyRateError_to_json_value_0(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy value = 0"""
        details = {"value": 0}
        error = InvalidHourlyRateError(details=details)
        result = error.to_json()
        assert result["error_code"] == "invalid_hourly_rate"
        assert result["http_status"] == 422
        assert result["message"] == InvalidHourlyRateError.default_message
        assert result["details"] == details


    ## Like we talked on our classes, all exception tests can be simplified.
    ## It's not like your tests are invalid, but does not comply with DRY rules (yes, for tests it also applies)
    ## This example contains almost all Exceptions (which of course should be within different files)
    ## But just for showcase, I've implemented them here to show you the principle of @pytest.mark.parametrize
    ## Oh and btw, you got typo in InvalidHourdlyRateError, it should be Hourly not Hourdly

    @pytest.mark.parametrize(
        (
                "error_class",
                "expected_error_id",
                "expected_error_code",
                "expected_http_status",
                "expected_default_message",
        ),
        [
            pytest.param(
                InvalidExchangeRateError,
                "ERR-FIN-01",
                "invalid_exchange_rate",
                422,
                "The exchange rate is incorrect, <=0",
                id="invalid_exchange_rate",
            ),
            pytest.param(
                InvalidHourlyRateError,
                "ERR-FIN-02",
                "invalid_hourly_rate",
                422,
                "The hourly rate is incorrect, <=0",
                id="invalid_hourly_rate",
            ),
            pytest.param(
                InvalidTaskTimeRangeError,
                "ERR-TIME-01",
                "invalid_task_time_range",
                400,
                "The start time of a task cannot be later than stop time",
                id="invalid_task_time_range",
            ),
            pytest.param(
                TaskOverlapError,
                "ERR-TIME-02",
                "task_overlap",
                409,
                "One task overlaps with another",
                id="task_overlap",
            ),
            pytest.param(
                TaskLockedError,
                "ERR-AUTH-01",
                "task_locked",
                403,
                "The task is locked. It cannot be modified.",
                id="task_locked",
            ),
            pytest.param(
                MissingCalculationDataError,
                "ERR-DATA-01",
                "missing_calculation_data",
                400,
                "Lack of data needed to calculate costs",
                id="missing_calculation_data",
            ),
            pytest.param(
                ProjectInUseError,
                "ERR-REF-01",
                "project_in_use",
                409,
                "You cannot delete the project. It is in use in another task.",
                id="project_in_use",
            ),
            pytest.param(
                EntityNotFoundError,
                "ERR-REF-02",
                "entity_not_found",
                404,
                "The entity was not found.",
                id="entity_not_found",
            ),
            pytest.param(
                NbpApiUnavailableError,
                "ERR-INT-01",
                "nbp_api_unavailable",
                503,
                "Unable to connect to the NBP API",
                id="nbp_api_unavailable",
            ),
            pytest.param(
                GenericSystemError,
                "ERR-GENERIC-01",
                "internal_error",
                500,
                "System error",
                id="generic_system_error",
            ),
        ],
    )
    def test_business_error_contract(
            self,
            error_class,
            expected_error_id,
            expected_error_code,
            expected_http_status,
            expected_default_message,
    ) -> None:
        assert error_class.error_id == expected_error_id
        assert error_class.error_code == expected_error_code
        assert error_class.http_status == expected_http_status
        assert error_class.default_message == expected_default_message