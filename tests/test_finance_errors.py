import pytest
from tests import InvalidHourlyRateError, InvalidExchangeRateError


class TestBusinessErrorContracts:

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
