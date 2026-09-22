"""Unit tests for backtesting_utils — all assertions, no print-and-pray."""

import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Validation tests — no network required
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_empty_tickers_returns_error(self):
        from backtesting_utils import safe_portfolio_backtest

        result, error, warning = safe_portfolio_backtest([], [], "SPY")

        assert result is None
        assert error is not None
        assert "empty" in error.lower()

    def test_allocations_not_summing_to_1_returns_error(self):
        from backtesting_utils import safe_portfolio_backtest

        result, error, warning = safe_portfolio_backtest(
            ["AAPL", "MSFT"], [0.6, 0.3], "SPY"
        )

        assert result is None
        assert error is not None
        assert "100" in error or "sum" in error.lower()

    def test_single_ticker_full_allocation_passes_validation(self):
        """Allocation of exactly 1.0 should not trigger the validation error."""
        from backtesting_utils import safe_portfolio_backtest

        # We don't care about the network result here — just that validation passes
        # and the error is NOT the allocation message.
        with patch("backtesting_utils._download_data_with_retries") as mock_dl:
            mock_dl.side_effect = Exception("network disabled in unit test")
            result, error, warning = safe_portfolio_backtest(
                ["AAPL"], [1.0], "SPY", start_date="2023-01-01"
            )

        assert error != "Allocations must sum to 100%. Current sum: 100.00%"

    def test_allocation_sum_exactly_at_tolerance_boundary(self):
        """Sum within 0.01 of 1.0 should pass validation."""
        from backtesting_utils import safe_portfolio_backtest

        with patch("backtesting_utils._download_data_with_retries") as mock_dl:
            mock_dl.side_effect = Exception("network disabled in unit test")
            result, error, warning = safe_portfolio_backtest(
                ["AAPL", "MSFT"], [0.5, 0.501], "SPY", start_date="2023-01-01"
            )

        # Validation should pass (sum ≈ 1.001, within 0.01 tolerance)
        assert "sum" not in (error or "").lower()

    def test_allocation_sum_outside_tolerance_returns_error(self):
        from backtesting_utils import safe_portfolio_backtest

        result, error, warning = safe_portfolio_backtest(
            ["AAPL", "MSFT"], [0.3, 0.3], "SPY"
        )

        assert result is None
        assert error is not None
        # Should mention the actual sum
        assert "60.00%" in error


# ---------------------------------------------------------------------------
# get_company_name tests — mock yfinance
# ---------------------------------------------------------------------------

class TestGetCompanyName:
    def test_returns_long_name_when_available(self):
        from backtesting_utils import get_company_name

        mock_info = {"longName": "Apple Inc.", "shortName": "Apple", "symbol": "AAPL"}
        with patch("yfinance.Ticker") as mock_ticker:
            mock_ticker.return_value.info = mock_info
            name = get_company_name("AAPL")

        assert name == "Apple Inc."

    def test_falls_back_to_short_name(self):
        from backtesting_utils import get_company_name

        mock_info = {"longName": None, "shortName": "Apple", "symbol": "AAPL"}
        with patch("yfinance.Ticker") as mock_ticker:
            mock_ticker.return_value.info = mock_info
            name = get_company_name("AAPL")

        assert name == "Apple"

    def test_falls_back_to_ticker_symbol_when_all_names_missing(self):
        from backtesting_utils import get_company_name

        mock_info = {"longName": None, "shortName": None, "symbol": None}
        with patch("yfinance.Ticker") as mock_ticker:
            mock_ticker.return_value.info = mock_info
            name = get_company_name("AAPL")

        assert name == "AAPL"

    def test_truncates_long_names(self):
        from backtesting_utils import get_company_name

        long_name = "A" * 40
        mock_info = {"longName": long_name, "shortName": None, "symbol": None}
        with patch("yfinance.Ticker") as mock_ticker:
            mock_ticker.return_value.info = mock_info
            name = get_company_name("LONGCO")

        assert len(name) <= 30
        assert name.endswith("...")

    def test_returns_fallback_on_exception(self):
        from backtesting_utils import get_company_name

        with patch("yfinance.Ticker") as mock_ticker:
            mock_ticker.return_value.info = property(
                lambda self: (_ for _ in ()).throw(RuntimeError("network error"))
            )
            mock_ticker.side_effect = RuntimeError("network error")
            name = get_company_name("AAPL")

        assert name == "Name not found"


# ---------------------------------------------------------------------------
# Backtest core logic — mock yfinance + bt
# ---------------------------------------------------------------------------

def _make_price_series(ticker: str, n: int = 60) -> pd.Series:
    """Generate a fake daily price series."""
    dates = pd.bdate_range(end=datetime.today(), periods=n)
    prices = 100 * (1 + np.random.randn(n).cumsum() * 0.01)
    return pd.Series(prices, index=dates, name=ticker)


class TestSafePortfolioBacktest:
    def _mock_download(self, tickers, start_date):
        """Return fake OHLCV close data for the requested tickers."""
        series = [_make_price_series(t) for t in tickers]
        df = pd.concat(series, axis=1)
        df.columns = tickers
        return df

    def test_valid_single_ticker_returns_no_error(self):
        from backtesting_utils import safe_portfolio_backtest

        with patch("backtesting_utils._download_data_with_retries", side_effect=self._mock_download), \
             patch("bt.run") as mock_run:
            mock_results = MagicMock()
            mock_run.return_value = mock_results

            result, error, warning = safe_portfolio_backtest(
                ["AAPL"], [1.0], "SPY", start_date="2023-01-01"
            )

        assert error is None

    def test_failed_benchmark_download_returns_error(self):
        from backtesting_utils import safe_portfolio_backtest
        import yfinance

        def selective_fail(tickers, start_date):
            if tickers == ["SPY"]:
                raise yfinance.exceptions.YFPricesMissingError("SPY: no data")
            return self._mock_download(tickers, start_date)

        with patch("backtesting_utils._download_data_with_retries", side_effect=selective_fail):
            result, error, warning = safe_portfolio_backtest(
                ["AAPL"], [1.0], "SPY", start_date="2023-01-01"
            )

        assert result is None
        assert error is not None
        assert "SPY" in error

    def test_returns_three_tuple_always(self):
        """safe_portfolio_backtest must always return (result, error, warning)."""
        from backtesting_utils import safe_portfolio_backtest

        output = safe_portfolio_backtest([], [], "SPY")

        assert isinstance(output, tuple)
        assert len(output) == 3

    def test_insufficient_data_returns_error(self):
        from backtesting_utils import safe_portfolio_backtest

        def tiny_download(tickers, start_date):
            series = [_make_price_series(t, n=5) for t in tickers]
            df = pd.concat(series, axis=1)
            df.columns = tickers
            return df

        with patch("backtesting_utils._download_data_with_retries", side_effect=tiny_download):
            result, error, warning = safe_portfolio_backtest(
                ["AAPL"], [1.0], "SPY", start_date="2024-01-01"
            )

        assert result is None
        assert error is not None
        assert "20" in error or "insufficient" in error.lower()


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

class TestCLIArgumentParsing:
    def test_cli_rejects_mismatched_tickers_and_allocations(self, capsys):
        from cli_dashboard import run_cli_backtest

        run_cli_backtest("AAPL,MSFT", "100", "SPY")

        captured = capsys.readouterr()
        assert "Error" in captured.out or "error" in captured.out.lower()

    def test_cli_normalises_ticker_to_uppercase(self):
        """Tickers entered in lowercase must be uppercased before use."""
        from cli_dashboard import run_cli_backtest

        with patch("cli_dashboard.safe_portfolio_backtest") as mock_bt, \
             patch("cli_dashboard.get_company_name", return_value="Apple Inc."):
            mock_bt.return_value = (None, "network disabled", None)
            run_cli_backtest("aapl", "100", "spy")
            call_args = mock_bt.call_args[0]

        assert call_args[0] == ["AAPL"]
        assert call_args[2] == "spy"  # benchmark is passed through as-is by CLI

    def test_cli_converts_percentage_allocations_to_fractions(self):
        """CLI takes percentages (60,40) and converts to fractions (0.6, 0.4)."""
        from cli_dashboard import run_cli_backtest

        with patch("cli_dashboard.safe_portfolio_backtest") as mock_bt, \
             patch("cli_dashboard.get_company_name", return_value="Apple Inc."):
            mock_bt.return_value = (None, "network disabled", None)
            run_cli_backtest("AAPL,MSFT", "60,40", "SPY")
            call_args = mock_bt.call_args[0]

        allocations = call_args[1]
        assert abs(allocations[0] - 0.60) < 1e-9
        assert abs(allocations[1] - 0.40) < 1e-9


# ---------------------------------------------------------------------------
# Live integration tests — skipped unless --network flag passed
# ---------------------------------------------------------------------------

@pytest.mark.network
class TestLiveNetwork:
    def test_aapl_single_stock_backtest(self):
        from backtesting_utils import safe_portfolio_backtest

        result, error, warning = safe_portfolio_backtest(
            ["AAPL"], [1.0], "SPY", start_date="2022-01-01"
        )

        assert error is None, f"Unexpected error: {error}"
        assert result is not None

    def test_invalid_ticker_returns_error(self):
        from backtesting_utils import safe_portfolio_backtest

        result, error, warning = safe_portfolio_backtest(
            ["INVALIDTICKER_XYZ"], [1.0], "SPY", start_date="2022-01-01"
        )

        assert result is None
        assert error is not None
