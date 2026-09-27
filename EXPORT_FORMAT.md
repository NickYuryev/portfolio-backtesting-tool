# Export formats

## Portfolio (`portfolio_allocation.csv`)

```csv
Ticker,Company Name,Weight (%)
AAPL,Apple Inc.,30.00
GOOGL,Alphabet Inc.,25.00
MSFT,Microsoft Corporation,25.00
AMZN,Amazon.com Inc.,20.00
```

The same format imports back in.

## Backtest report (`backtest_comprehensive_report.csv`)

One file with three sections, each starting with a title line and separated
by blank lines.

**PORTFOLIO PERFORMANCE TIME SERIES.** One row per trading day, both series
rebased to 100 on the first day:

```csv
Date,Portfolio Value (Base=100),Benchmark SPY (Base=100)
2020-01-02,100.00,100.00
2020-01-03,101.25,100.87
```

**KEY PERFORMANCE METRICS.** A short summary: annualized return, return relative to the benchmark, volatility, correlation with the
benchmark, and best and worst year, for the portfolio and the benchmark.

**DETAILED STATISTICS.** Everything `bt` reports, with keys as `bt` names
them (`cagr`, `max_drawdown`, `daily_sharpe`, `monthly_vol`,
`avg_drawdown_days`, and so on). These are raw fractions, so 0.15 means 15%.

## Reading the time series in pandas

The sections share one file, so split on the first blank line after the
table:

```python
import io
import pandas as pd

text = open("backtest_comprehensive_report.csv").read()
series_block = text.split("\n\n")[1]
df = pd.read_csv(io.StringIO(series_block), parse_dates=["Date"])
```
