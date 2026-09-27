# Portfolio Backtesting Dashboard

A Dash app for backtesting a weighted portfolio against a benchmark using
Yahoo Finance data. It works with anything yfinance can price: stocks, ETFs,
futures, currencies and indices.

[![CI](https://github.com/NickYuryev/portfolio-backtesting-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/NickYuryev/portfolio-backtesting-tool/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)

## Running it

With Docker:

```bash
docker compose up -d
```

Or locally (Python 3.10+):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python dashboard.py
```

Either way the dashboard is at http://localhost:8050.

## Using it

1. Add tickers and set their weights. The total has to come to 100%.
2. Pick a benchmark (SPY by default) and, optionally, a start date in
   `YYYY-MM-DD` form. If you leave it blank, the backtest starts at the latest
   first-available date across your tickers, so every holding has data from
   day one.
3. Run the backtest. You get a growth chart (log scale toggle included),
   quarterly returns, and a metrics table: annualized return, return relative
   to the benchmark, volatility, Sharpe, Sortino, CAGR, max drawdown,
   correlation, and best and worst year.

Portfolios are also saved to `portfolio_cache/`, which keeps the last five.

Ticker formats follow Yahoo Finance, for example `AAPL`, `GC=F` (gold
futures), `EURUSD=X`, `^GSPC`, `BP.L`, `7203.T`.

### Import and export

Portfolios import and export as CSV:

```csv
Ticker,Company Name,Weight (%)
AAPL,Apple Inc.,30.00
MSFT,Microsoft Corporation,70.00
```

Only `Ticker` and `Weight (%)` are required on import. After a backtest you can
also export a full report with the daily series, the headline metrics and the
complete `bt` statistics. See [EXPORT_FORMAT.md](EXPORT_FORMAT.md) for the
layout.

### Command line

```bash
python cli_dashboard.py --tickers AAPL,GOOGL,MSFT --allocations 40,30,30 \
  --benchmark SPY --start_date 2020-01-01
```

Installing the package (`pip install .`) also gives you a `backtest` command
with the same flags.

## Code layout

| File | Purpose |
|---|---|
| `dashboard.py` | App entry point, also exposes `server` for gunicorn |
| `dashboard_layout.py` | Page layout |
| `dashboard_callbacks.py` | Dash callbacks |
| `dashboard_utils.py` | Portfolio cache and display helpers |
| `portfolio_io.py` | CSV import and report export |
| `backtesting_utils.py` | Data download (with retries) and the `bt` backtest |
| `cli_dashboard.py` | Command-line runner |
| `tests/` | pytest suite |

## Development

```bash
pip install -r requirements-dev.txt
make test          # unit tests, no network
make test-network  # also runs the tests that call yfinance
make lint          # ruff
make fmt           # black and ruff --fix
```

CI runs lint and tests on Python 3.10 to 3.12 and checks that the Docker image
builds.

## License

[Apache 2.0](LICENSE)
