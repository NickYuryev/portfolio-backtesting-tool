# Portfolio Backtesting Dashboard

A comprehensive, professional-grade portfolio backtesting tool with support for stocks, ETFs, commodities, currencies, and indices from Yahoo Finance. Features include CSV import/export, advanced performance metrics, log scale visualization, and comprehensive data export capabilities.

![Dashboard Preview](https://img.shields.io/badge/status-production--ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 Features

### Core Functionality
- **Universal Asset Support**: Stocks, ETFs, commodities, currencies, indices - anything on Yahoo Finance
- **Intelligent Date Handling**: Automatically uses the latest common start date among all tickers
- **Real-time Data**: Fetches current market data via yfinance API
- **Portfolio Optimization**: Test different allocation strategies with ease

### Advanced Features
- **CSV Import/Export**: Save and load portfolio allocations
- **Comprehensive Data Export**: Export time-series data and metrics for custom analysis
- **Log Scale Visualization**: Toggle between linear and logarithmic scales
- **Robust Error Handling**: Graceful handling of missing tickers and API failures
- **Portfolio Caching**: Automatically saves recent portfolios for quick access

### Performance Metrics
- Annualized Returns
- Volatility (Standard Deviation)
- Sharpe & Sortino Ratios
- CAGR (Compound Annual Growth Rate)
- Maximum Drawdown
- Correlation with Benchmark
- Best/Worst Year Returns
- Quarterly Returns Visualization
- 30+ Additional Statistical Metrics

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for fetching market data)

## 🚀 Quick Start

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Running the Dashboard

```bash
python dashboard.py
```

The dashboard will be available at: **http://127.0.0.1:8050**

Open this URL in your web browser to start using the dashboard.

## 📖 User Guide

### Building a Portfolio

#### Method 1: Manual Entry

1. **Add Holdings**:
   - Enter a ticker symbol (e.g., `AAPL`, `SPY`, `GC=F`)
   - Click "**+ Add Holding**"
   - Adjust the weight percentage

2. **Set Allocations**:
   - Modify weight percentages using the input fields
   - Ensure total allocation equals 100% (shown at bottom)
   - Portfolio auto-saves to cache

3. **Configure Backtest**:
   - Set benchmark ticker (default: SPY)
   - Optionally set start date (format: YYYY-MM-DD)
   - Leave start date blank for automatic detection

4. **Run Backtest**:
   - Click "**Run Backtest**"
   - View results in the right panel

#### Method 2: CSV Import

1. **Prepare CSV File**:
```csv
Ticker,Company Name,Weight (%)
AAPL,Apple Inc.,30.00
GOOGL,Alphabet Inc.,25.00
MSFT,Microsoft Corporation,25.00
AMZN,Amazon.com Inc.,20.00
```

2. **Import**:
   - Click "**📁 Import CSV**"
   - Select your CSV file
   - Portfolio loads automatically

3. **Download Template**:
   - Click "**📋 Sample CSV**" for a template

### Supported Ticker Formats

The dashboard supports all Yahoo Finance tickers:

| Asset Type | Example Tickers | Notes |
|------------|----------------|-------|
| **US Stocks** | `AAPL`, `GOOGL`, `MSFT` | Standard symbols |
| **ETFs** | `SPY`, `QQQ`, `VTI` | All major ETFs |
| **Commodities** | `GC=F`, `CL=F`, `SI=F` | Gold, Oil, Silver |
| **Currencies** | `EURUSD=X`, `GBPUSD=X` | Forex pairs |
| **Indices** | `^GSPC`, `^DJI`, `^IXIC` | S&P 500, Dow, NASDAQ |
| **International** | `BP.L`, `TD.TO`, `7203.T` | London, Toronto, Tokyo |

### Exporting Data

#### Export Portfolio Allocations
- Click "**💾 Export CSV**"
- Downloads: `portfolio_allocation.csv`
- Use for backup, sharing, or re-importing

#### Export Full Report
- Run a backtest first
- Click "**📊 Export Full Report (Metrics + Data)**"
- Downloads: `backtest_comprehensive_report.csv`
- Contains:
  - Time-series performance data (every trading day)
  - Key performance metrics table
  - Detailed statistics (30+ metrics)

### Visualizations

#### Performance Chart
- Shows portfolio vs benchmark over time
- Values normalized to 100 at start
- Toggle log scale with "**Toggle Log Scale**" button
- Hover for detailed values

#### Quarterly Returns
- Bar chart of quarterly performance
- Green for positive, red for negative returns
- Helps identify seasonal patterns

### Performance Metrics Explained

| Metric | Description | What It Means |
|--------|-------------|---------------|
| **Annualized Return** | Average yearly return | Higher is better |
| **Relative Return** | Outperformance vs benchmark | Positive means you beat the benchmark |
| **Volatility (Std Dev)** | Price fluctuation measure | Lower is less risky |
| **Sharpe Ratio** | Risk-adjusted returns | Higher is better (>1 is good) |
| **Sortino Ratio** | Downside risk-adjusted returns | Like Sharpe but only penalizes losses |
| **CAGR** | Compound annual growth rate | Smoothed long-term return |
| **Max Drawdown** | Largest peak-to-trough decline | Lower is better (less loss) |
| **Correlation** | How closely portfolio follows benchmark | 0-1 scale, 1 = identical |
| **Best/Worst Year** | Annual extremes | Shows range of outcomes |

## 📊 Analyzing Exported Data

### In Excel/Google Sheets

1. Open the `backtest_comprehensive_report.csv`
2. Data is organized in three sections:
   - **Section 1**: Time-series data (create charts)
   - **Section 2**: Key metrics (quick summary)
   - **Section 3**: Detailed statistics (in-depth analysis)

3. Create custom charts:
   - Select the time-series data
   - Insert → Chart → Line Chart
   - Compare portfolio vs benchmark

### In Python

```python
import pandas as pd
import matplotlib.pyplot as plt

# Read time-series data (skip header rows)
df = pd.read_csv('backtest_comprehensive_report.csv', skiprows=2)

# Parse dates
df['Date'] = pd.to_datetime(df['Date'])

# Plot performance
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Portfolio Value (Base=100)'], label='Portfolio')
plt.plot(df['Date'], df['Benchmark SPY (Base=100)'], label='Benchmark')
plt.xlabel('Date')
plt.ylabel('Value (Base = 100)')
plt.title('Portfolio Performance')
plt.legend()
plt.grid(True)
plt.show()

# Calculate additional metrics
df['Daily Return'] = df['Portfolio Value (Base=100)'].pct_change()
print(f"Average Daily Return: {df['Daily Return'].mean():.4f}%")
```

### In R

```r
library(tidyverse)
library(lubridate)

# Read data
data <- read_csv('backtest_comprehensive_report.csv', skip = 2)

# Parse dates
data$Date <- ymd(data$Date)

# Create plot
ggplot(data, aes(x = Date)) +
  geom_line(aes(y = `Portfolio Value (Base=100)`, color = "Portfolio")) +
  geom_line(aes(y = `Benchmark SPY (Base=100)`, color = "Benchmark")) +
  labs(title = "Portfolio Performance",
       x = "Date",
       y = "Value (Base = 100)") +
  theme_minimal() +
  scale_color_manual(values = c("Portfolio" = "blue", "Benchmark" = "gray"))
```

## 🗂️ Project Structure

```
improved backtesting/
├── 📄 Core Application
│   ├── dashboard.py              # Main entry point
│   ├── dashboard_layout.py       # UI components
│   ├── dashboard_callbacks.py    # Business logic & callbacks
│   ├── dashboard_utils.py        # Helper functions
│   ├── portfolio_io.py           # CSV import/export
│   └── backtesting_utils.py      # Backtest engine
│
├── 📄 CLI Tools
│   ├── cli_dashboard.py          # Command-line interface
│   └── test_cli_dashboard.py     # CLI tests
│
├── 📄 Documentation
│   ├── README.md                 # This file
│   ├── README_REFACTOR.md        # Technical refactoring details
│   ├── REFACTOR_SUMMARY.md       # Refactoring overview
│   └── EXPORT_FORMAT.md          # Export format specifications
│
├── 📄 Configuration
│   ├── requirements.txt          # Python dependencies
│   └── .gitignore               # Git ignore rules
│
└── 📁 Generated (not in git)
    └── portfolio_cache/          # Cached portfolios
```

## 🛠️ Advanced Usage

### Command-Line Interface

For automated backtesting:

```bash
python cli_dashboard.py \
  --tickers AAPL,GOOGL,MSFT \
  --allocations 40,30,30 \
  --benchmark SPY \
  --start_date 2020-01-01
```

### Custom Start Dates

Leave blank for automatic detection (recommended), or specify:

```
2020-01-01    # Full date
2020-01       # First day of month
2020          # First day of year
```

### Comparing Multiple Strategies

1. Run backtest for Strategy A
2. Export full report → `strategy_a.csv`
3. Change allocations for Strategy B
4. Export full report → `strategy_b.csv`
5. Merge and compare in Excel/Python

## ⚠️ Troubleshooting

### "Ticker Not Found" Error
- Verify ticker on [Yahoo Finance](https://finance.yahoo.com/)
- Check for correct suffix (`.L` for London, `.TO` for Toronto, etc.)
- Some tickers have limited historical data

### Import Failed
- Ensure CSV has `Ticker` and `Weight (%)` columns
- Check that weights are numbers (not text)
- Verify file is UTF-8 encoded
- Weights should sum to 100% (±1% tolerance)

### Backtest Errors
- Ensure all tickers have overlapping date ranges
- Check internet connection
- Verify allocations sum to 100%
- Try a more recent start date if data is sparse

### Performance Issues
- Reduce the number of tickers (< 20 recommended)
- Use a more recent start date
- Check your internet connection speed
- Clear portfolio cache: delete `portfolio_cache/` folder

## 🔧 Configuration

### Changing the Port

Edit `dashboard.py`:
```python
app.run(debug=False, host='127.0.0.1', port=8050)  # Change 8050 to desired port
```

### Enabling Debug Mode

Edit `dashboard.py`:
```python
app.run(debug=True, host='127.0.0.1', port=8050)  # Set debug=True
```

⚠️ **Note**: Debug mode should only be used for development.

### Adjusting Cache Size

Edit `dashboard_utils.py`:
```python
if len(cache_files) > 5:  # Change 5 to desired number
```

## 📦 Dependencies

- **dash**: Web application framework
- **plotly**: Interactive charts
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **yfinance**: Yahoo Finance API
- **bt**: Backtesting library
- **tenacity**: Retry logic for API calls

See `requirements.txt` for specific versions.

## 🤝 Contributing

This is a personal project, but suggestions are welcome! Feel free to:
- Report bugs
- Suggest features
- Share interesting portfolio strategies

## 📄 License

MIT License - Feel free to use and modify as needed.

## 🙏 Acknowledgments

- **yfinance**: For providing free financial data
- **bt**: For the robust backtesting framework
- **Plotly/Dash**: For the excellent visualization tools

## 📧 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the `EXPORT_FORMAT.md` for export details
3. See `README_REFACTOR.md` for technical details

## 🎯 Example Portfolios to Try

### Conservative (Low Risk)
```csv
Ticker,Weight (%)
BND,40.00
VTI,35.00
VXUS,25.00
```

### Aggressive Growth (High Risk)
```csv
Ticker,Weight (%)
QQQ,40.00
ARKK,30.00
TSLA,20.00
NVDA,10.00
```

### Balanced
```csv
Ticker,Weight (%)
SPY,50.00
AGG,30.00
GLD,10.00
VNQ,10.00
```

### Commodities Focus
```csv
Ticker,Weight (%)
GLD,30.00
GC=F,25.00
USO,25.00
DBA,20.00
```

---

**Happy Backtesting! 📈**
