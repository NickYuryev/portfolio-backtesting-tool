# Portfolio Backtesting Dashboard - Refactored

## Overview
A comprehensive portfolio backtesting tool with support for world tickers, commodities, and all yfinance-supported assets. Features include CSV import/export, robust error handling, log scale visualization, and comprehensive performance metrics.

## New Modular Structure

### Core Files

#### `dashboard.py` (Main Application)
- Entry point for the application
- Minimal, clean code that ties everything together
- Initializes the app and registers callbacks

#### `dashboard_layout.py` (UI Layout)
- Contains all UI components and layout definitions
- Separated into logical functions:
  - `create_layout()` - Main layout
  - `create_portfolio_builder()` - Left panel
  - `create_results_panel()` - Right panel

#### `dashboard_callbacks.py` (Business Logic)
- All callback functions
- Organized into sections:
  - Portfolio management (add, remove, update holdings)
  - Backtest execution and results display
  - Import/Export functionality
  - Chart generation
  - Metrics calculation

#### `dashboard_utils.py` (Helper Functions)
- Utility functions for common operations:
  - Cache management (save/load portfolios)
  - Formatting functions
  - Logging utilities
  - HTML component builders

#### `portfolio_io.py` (Import/Export)
- CSV import/export functionality
- Portfolio format validation
- Sample CSV generation
- File parsing and encoding

#### `backtesting_utils.py` (Backtest Engine)
- Core backtesting logic
- Yahoo Finance data fetching with retry logic
- Error handling for missing/invalid tickers
- Automatic date range detection (uses latest common start date)

## New Features

### 1. CSV Import/Export
- **Export Portfolio**: Save current allocations to CSV with ticker, company name, and weight
- **Import Portfolio**: Load allocations from CSV file
- **Sample CSV**: Download a template with example format
- **Export Metrics**: Export backtest performance metrics to CSV

### 2. Enhanced Error Handling
- Graceful handling of missing tickers
- Clear error messages
- Retry logic for API failures
- Validation of allocations

### 3. Log Scale Toggle
- Switch between linear and logarithmic chart scales
- Useful for visualizing large percentage changes
- No data recalculation (pure visualization change)

### 4. Automatic Start Date
- Uses the latest common start date among all tickers
- Ensures all holdings have data for the entire backtest period
- Can be overridden with custom start date

## CSV Format

### Portfolio CSV Format
```csv
Ticker,Company Name,Weight (%)
AAPL,Apple Inc.,30.00
GOOGL,Alphabet Inc.,25.00
MSFT,Microsoft Corporation,25.00
AMZN,Amazon.com Inc.,20.00
```

**Requirements:**
- Must have `Ticker` and `Weight (%)` columns
- `Company Name` is optional (will be fetched if missing)
- Weights should sum to 100% (tolerance of ±1%)
- Tickers should be valid Yahoo Finance symbols

### Metrics CSV Format
Exported metrics include:
- Annualized Return
- Volatility (Std Dev)
- Sharpe Ratio
- Sortino Ratio
- CAGR
- Max Drawdown
- Best/Worst Year
- Correlation with Benchmark
- And more...

## Usage

### Running the Dashboard
```bash
python dashboard.py
```

The dashboard will be available at `http://127.0.0.1:8050`

### Adding Holdings
1. Enter a ticker symbol (e.g., AAPL, GC=F for gold, ^GSPC for S&P 500)
2. Click "Add Holding"
3. Adjust weight percentages as needed
4. Ensure total allocation equals 100%

### Importing Portfolio
1. Prepare a CSV file with the required format
2. Click "Import CSV" button
3. Select your file
4. Portfolio will be loaded automatically

### Exporting Portfolio
1. Build your portfolio
2. Click "Export CSV" to download current allocations
3. Click "Export Metrics to CSV" after running a backtest to download performance data

### Running Backtest
1. Add holdings (total must equal 100%)
2. Set benchmark ticker (default: SPY)
3. Optionally set start date (leave blank for automatic)
4. Click "Run Backtest"
5. Toggle log scale to change chart visualization

## Supported Assets

The dashboard supports all Yahoo Finance tickers including:
- **Stocks**: AAPL, GOOGL, MSFT, etc.
- **ETFs**: SPY, QQQ, VTI, etc.
- **Commodities**: GC=F (gold), CL=F (crude oil), SI=F (silver), etc.
- **Currencies**: EURUSD=X, GBPUSD=X, etc.
- **Indices**: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ), etc.
- **International**: Use appropriate suffixes (.L for London, .TO for Toronto, etc.)

## File Organization

```
improved backtesting/
├── dashboard.py              # Main application entry point
├── dashboard_layout.py       # UI layout definitions
├── dashboard_callbacks.py    # Callback functions
├── dashboard_utils.py        # Utility functions
├── portfolio_io.py           # CSV import/export
├── backtesting_utils.py      # Backtesting engine
├── cli_dashboard.py          # Command-line interface
├── test_cli_dashboard.py     # CLI tests
├── requirements.txt          # Python dependencies
├── portfolio_cache/          # Cached portfolios (auto-created)
├── dashboard_debug.log       # Debug logs
└── dashboard_old_backup.py   # Backup of original dashboard
```

## Performance Metrics Explained

- **Annualized Return**: Average yearly return over the period
- **Volatility (Std Dev)**: Measure of price fluctuation
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
- **Sortino Ratio**: Like Sharpe but only penalizes downside volatility
- **CAGR**: Compound Annual Growth Rate
- **Max Drawdown**: Largest peak-to-trough decline
- **Correlation**: How closely portfolio follows benchmark (0-1)
- **Best/Worst Year**: Highest and lowest annual returns

## Troubleshooting

### Ticker Not Found
- Verify ticker symbol on Yahoo Finance
- Check for correct suffix for international stocks
- Some tickers may have limited history

### Import Failed
- Ensure CSV has required columns
- Check that weights are valid numbers
- Verify file is properly formatted UTF-8

### Backtest Errors
- Ensure all tickers have overlapping date ranges
- Check that allocations sum to 100%
- Verify internet connection for data download

## CLI Usage

For command-line backtesting:
```bash
python cli_dashboard.py --tickers AAPL,GOOGL --allocations 60,40 --benchmark SPY
```

## Development

### Adding New Features
1. UI components → `dashboard_layout.py`
2. Business logic → `dashboard_callbacks.py`
3. Helper functions → `dashboard_utils.py`
4. Backtest logic → `backtesting_utils.py`

### Running Tests
```bash
python test_cli_dashboard.py
```

## Dependencies

See `requirements.txt` for full list:
- dash
- plotly
- pandas
- numpy
- yfinance
- bt (backtest library)
- tenacity (retry logic)

## License

MIT License - Feel free to use and modify as needed.

