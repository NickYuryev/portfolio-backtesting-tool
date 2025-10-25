# Export Formats Guide

## Portfolio Allocation Export

**Button:** 💾 Export CSV  
**Filename:** `portfolio_allocation.csv`

### Format
```csv
Ticker,Company Name,Weight (%)
AAPL,Apple Inc.,30.00
GOOGL,Alphabet Inc.,25.00
MSFT,Microsoft Corporation,25.00
AMZN,Amazon.com Inc.,20.00
```

**Use Cases:**
- Backup your portfolio allocations
- Share portfolios with others
- Edit in Excel/Sheets and re-import
- Track portfolio changes over time

---

## Comprehensive Backtest Report Export

**Button:** 📊 Export Full Report (Metrics + Data)  
**Filename:** `backtest_comprehensive_report.csv`

### Sections

#### Section 1: Portfolio Performance Time Series
Contains date-by-date performance data normalized to base 100.

```csv
PORTFOLIO PERFORMANCE TIME SERIES
Data shows portfolio value normalized to 100 at start

Date,Portfolio Value (Base=100),Benchmark SPY (Base=100)
2020-01-02,100.00,100.00
2020-01-03,101.25,100.87
2020-01-06,102.50,101.45
...
```

**Use Cases:**
- Create custom charts in Excel/Python/R
- Perform additional statistical analysis
- Compare multiple portfolio versions
- Build custom visualizations

**Columns:**
- `Date`: Trading date (YYYY-MM-DD format)
- `Portfolio Value (Base=100)`: Your portfolio's performance
- `Benchmark {TICKER} (Base=100)`: Benchmark performance

#### Section 2: Key Performance Metrics
Summary table of the most important metrics displayed in the dashboard.

```csv
KEY PERFORMANCE METRICS

Metric,Portfolio,Benchmark
Annualized Return,15.23%,12.45%
Relative Return (vs Benchmark),+2.78%,—
Volatility (Std Dev),18.42%,16.35%
Correlation with Benchmark,0.8523,1.0000
Best Year,45.67%,38.92%
Worst Year,-12.34%,-15.67%
```

**Use Cases:**
- Quick comparison between portfolios
- Documentation and reporting
- Performance tracking over time
- Client reports

**Metrics Included:**
- Annualized Return (%)
- Relative Return vs Benchmark (%)
- Volatility/Standard Deviation (%)
- Correlation with Benchmark (0-1)
- Best Year (%)
- Worst Year (%)

#### Section 3: Detailed Statistics
Complete set of statistics from the backtest library.

```csv
DETAILED STATISTICS

Metric,Portfolio,Benchmark
start,2020-01-02,2020-01-02
end,2024-01-02,2024-01-02
rf,0.0,0.0
total_return,0.6547,0.5234
cagr,0.1523,0.1245
max_drawdown,-0.1234,-0.1567
calmar,1.2345,0.7945
mtd,0.0234,0.0189
three_month,0.0567,0.0445
six_month,0.0892,0.0723
ytd,0.1234,0.0987
one_year,0.1523,0.1245
three_year,0.4567,0.3789
five_year,0.6547,0.5234
ten_year,N/A,N/A
incep,0.6547,0.5234
daily_sharpe,0.8234,0.7612
daily_sortino,1.2345,1.0987
daily_mean,0.0006,0.0005
daily_vol,0.0073,0.0065
daily_skew,-0.1234,-0.2345
daily_kurt,3.4567,3.2345
best_day,0.0534,0.0489
worst_day,-0.0423,-0.0512
monthly_sharpe,0.8456,0.7823
monthly_sortino,1.2567,1.1234
monthly_mean,0.0125,0.0104
monthly_vol,0.0456,0.0412
monthly_skew,-0.2345,-0.3456
monthly_kurt,2.8901,2.6789
best_month,0.1234,0.0987
worst_month,-0.0876,-0.1123
yearly_sharpe,0.8234,0.7612
yearly_sortino,1.2345,1.0987
yearly_mean,0.1523,0.1245
yearly_vol,0.1842,0.1635
yearly_skew,0.1234,-0.0987
yearly_kurt,1.8901,1.6789
best_year,0.4567,0.3892
worst_year,-0.1234,-0.1567
avg_drawdown,-0.0534,-0.0612
avg_drawdown_days,23.45,28.67
avg_up_month,0.0456,0.0389
avg_down_month,-0.0389,-0.0445
win_year_perc,0.75,0.75
twelve_month_win_perc,0.6789,0.6234
```

**Use Cases:**
- In-depth statistical analysis
- Academic research
- Risk management analysis
- Compliance reporting

---

## Working with Exported Data

### Excel
1. Open the CSV file in Excel
2. Each section is clearly labeled
3. Use Excel's charting tools to create custom visualizations
4. Filter and analyze the time series data

### Python
```python
import pandas as pd

# Read the file
df = pd.read_csv('backtest_comprehensive_report.csv')

# The file has multiple sections, so you might want to parse them separately
# Or use pandas to read specific sections

# Example: Read just the time series (skip header rows)
time_series = pd.read_csv('backtest_comprehensive_report.csv', 
                          skiprows=2, 
                          nrows=None)  # Read until next section

# Create custom plots
import matplotlib.pyplot as plt
plt.plot(time_series['Date'], time_series['Portfolio Value (Base=100)'])
plt.show()
```

### R
```r
library(readr)
library(ggplot2)

# Read the file
data <- read_csv('backtest_comprehensive_report.csv', skip = 2)

# Create plots
ggplot(data, aes(x = Date)) +
  geom_line(aes(y = `Portfolio Value (Base=100)`, color = "Portfolio")) +
  geom_line(aes(y = `Benchmark SPY (Base=100)`, color = "Benchmark")) +
  theme_minimal()
```

---

## Tips

### Creating Custom Charts
- The time series data is normalized to 100, making it easy to compare
- Use log scale for portfolios with large percentage changes
- Calculate daily/monthly returns from the time series: `(Value[t] / Value[t-1]) - 1`

### Comparing Multiple Portfolios
1. Run backtests for different allocations
2. Export each report
3. Merge the time series data in Excel/Python
4. Create comparison charts

### Calculating Additional Metrics
With the time series data, you can calculate:
- Rolling Sharpe ratios
- Custom drawdown analysis
- Value at Risk (VaR)
- Maximum consecutive losses
- Win/loss streaks
- Custom correlation matrices

### Important Notes
- All percentage values are decimals multiplied by 100 (e.g., 15.23% is displayed as is)
- Dates are in YYYY-MM-DD format (ISO 8601)
- Values are normalized to base 100 for easy comparison
- The report includes the same data shown in the dashboard charts

