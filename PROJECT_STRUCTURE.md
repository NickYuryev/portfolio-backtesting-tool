# Project Structure

## Overview
This document describes the organization and architecture of the Portfolio Backtesting Dashboard.

## Directory Layout

```
improved backtesting/
│
├── 📄 Application Entry Point
│   └── dashboard.py                    # Main application file (37 lines)
│
├── 📄 Core Modules
│   ├── dashboard_layout.py             # UI layout definitions (209 lines)
│   ├── dashboard_callbacks.py          # Callback functions (637 lines)
│   ├── dashboard_utils.py              # Utility functions (209 lines)
│   ├── portfolio_io.py                 # CSV import/export (221 lines)
│   └── backtesting_utils.py            # Backtesting engine (180 lines)
│
├── 📄 Command-Line Tools
│   ├── cli_dashboard.py                # CLI interface (67 lines)
│   └── test_cli_dashboard.py           # CLI tests (121 lines)
│
├── 📄 Documentation
│   ├── README.md                       # Main user documentation
│   ├── README_REFACTOR.md              # Technical refactoring details
│   ├── REFACTOR_SUMMARY.md             # Refactoring summary
│   ├── EXPORT_FORMAT.md                # Export format specifications
│   └── PROJECT_STRUCTURE.md            # This file
│
├── 📄 Configuration
│   ├── requirements.txt                # Python dependencies
│   └── .gitignore                      # Git ignore patterns
│
└── 📁 Generated Files (ignored by git)
    ├── portfolio_cache/                # Cached portfolio data
    ├── __pycache__/                    # Python bytecode
    └── dashboard_debug.log             # Application logs
```

## Module Details

### dashboard.py
**Purpose**: Application entry point  
**Size**: 37 lines  
**Responsibilities**:
- Initialize Dash application
- Set up logging
- Create cache directory
- Load layout
- Register callbacks
- Start server

**Key Features**:
- Clean, minimal code
- Easy to understand
- Single point of configuration

### dashboard_layout.py
**Purpose**: UI components and layout  
**Size**: 209 lines  
**Responsibilities**:
- Define all HTML components
- Structure the dashboard layout
- Create import/export buttons
- Build left/right panels

**Key Functions**:
- `create_layout()` - Main layout builder
- `create_portfolio_builder()` - Left panel
- `create_results_panel()` - Right panel

**Design Principles**:
- Separation of concerns (UI separate from logic)
- Reusable components
- Consistent styling

### dashboard_callbacks.py
**Purpose**: Business logic and interactivity  
**Size**: 637 lines  
**Responsibilities**:
- Handle all user interactions
- Process portfolio updates
- Run backtests
- Generate visualizations
- Export data

**Key Callbacks**:
- `update_portfolio()` - Add/remove/modify holdings
- `update_backtest_results()` - Run backtest and display results
- `export_portfolio()` - Export allocations to CSV
- `export_metrics()` - Export comprehensive report
- `import_portfolio()` - Load CSV files

**Helper Functions**:
- `build_results_display()` - Construct results HTML
- `create_performance_chart()` - Build performance graph
- `create_quarterly_chart()` - Build quarterly returns
- `calculate_additional_metrics()` - Compute custom metrics
- `create_metrics_table()` - Build metrics table

### dashboard_utils.py
**Purpose**: Shared utility functions  
**Size**: 209 lines  
**Responsibilities**:
- Cache management
- Formatting functions
- Logging utilities
- HTML component builders

**Key Functions**:
- `save_portfolio_to_cache()` - Save portfolios
- `load_cached_portfolios()` - Load saved portfolios
- `format_portfolio_label()` - Format dropdown labels
- `log_event()` - Structured logging
- `create_portfolio_table_html()` - Build portfolio table
- `format_total_allocation()` - Format allocation display

### portfolio_io.py
**Purpose**: Import/export functionality  
**Size**: 221 lines  
**Responsibilities**:
- CSV file generation
- CSV file parsing
- Data validation
- Format conversion

**Key Functions**:
- `portfolio_to_csv()` - Export portfolio to CSV
- `csv_to_portfolio()` - Parse CSV to portfolio
- `parse_upload_content()` - Decode uploaded files
- `create_sample_csv()` - Generate template
- `create_comprehensive_metrics_csv()` - Export full report

**Data Formats**:
- Portfolio CSV: Simple ticker/weight format
- Metrics CSV: Multi-section comprehensive report

### backtesting_utils.py
**Purpose**: Core backtesting engine  
**Size**: 180 lines  
**Responsibilities**:
- Fetch market data from Yahoo Finance
- Run portfolio backtests
- Handle errors and retries
- Calculate performance metrics

**Key Functions**:
- `safe_portfolio_backtest()` - Main backtest function
- `get_company_name()` - Fetch ticker names
- `_download_data_with_retries()` - Robust data fetching

**Features**:
- Automatic retry logic (5 attempts)
- Exponential backoff
- Comprehensive error handling
- Latest common start date detection

### cli_dashboard.py
**Purpose**: Command-line interface  
**Size**: 67 lines  
**Responsibilities**:
- Parse command-line arguments
- Run backtests from terminal
- Display results in console

**Usage**:
```bash
python cli_dashboard.py --tickers AAPL,GOOGL --allocations 60,40
```

### test_cli_dashboard.py
**Purpose**: Automated testing  
**Size**: 121 lines  
**Responsibilities**:
- Test CLI functionality
- Verify backtest results
- Test error handling

## Data Flow

```
User Input → Callbacks → Backtest Engine → Results Display
     ↓                          ↓
  Cache ←------------------ Portfolio Data
     ↓
CSV Export
```

### Typical User Flow

1. **Portfolio Creation**:
   ```
   User Input → update_portfolio() → create_portfolio_table_html() → Display
   ```

2. **Running Backtest**:
   ```
   Button Click → update_backtest_results() → safe_portfolio_backtest() → 
   calculate_additional_metrics() → build_results_display() → Display
   ```

3. **Export**:
   ```
   Export Button → export_metrics() → create_comprehensive_metrics_csv() → 
   Download File
   ```

4. **Import**:
   ```
   Upload File → import_portfolio() → csv_to_portfolio() → 
   update_portfolio() → Display
   ```

## Architecture Principles

### 1. Separation of Concerns
- **Layout**: Pure UI (no business logic)
- **Callbacks**: Handles user interactions
- **Utils**: Reusable helper functions
- **IO**: File operations isolated
- **Engine**: Backtesting logic separate

### 2. Single Responsibility
Each module has one clear purpose:
- Layout → UI structure
- Callbacks → Interactivity
- Utils → Common operations
- IO → File handling
- Engine → Backtesting

### 3. Modularity
- Easy to modify one part without affecting others
- Clear interfaces between modules
- Testable components

### 4. Maintainability
- Well-organized code
- Clear naming conventions
- Comprehensive documentation
- Consistent styling

## Code Statistics

| Module | Lines | Purpose | Complexity |
|--------|-------|---------|------------|
| dashboard.py | 37 | Entry point | Low |
| dashboard_layout.py | 209 | UI | Low |
| dashboard_callbacks.py | 637 | Logic | Medium |
| dashboard_utils.py | 209 | Helpers | Low |
| portfolio_io.py | 221 | Import/Export | Medium |
| backtesting_utils.py | 180 | Engine | High |
| **Total** | **1,493** | **Full App** | **Medium** |

## Dependencies Graph

```
dashboard.py
    ↓
    ├── dashboard_layout.py
    ├── dashboard_utils.py
    └── dashboard_callbacks.py
            ↓
            ├── backtesting_utils.py
            ├── portfolio_io.py
            └── dashboard_utils.py
```

## Configuration Points

### 1. Server Configuration
**File**: `dashboard.py`
```python
app.run(debug=False, host='127.0.0.1', port=8050)
```

### 2. Cache Size
**File**: `dashboard_utils.py`
```python
if len(cache_files) > 5:  # Number of cached portfolios
```

### 3. Logging Level
**File**: `dashboard.py`
```python
logging.basicConfig(level=logging.DEBUG)  # Change to INFO or WARNING
```

### 4. Retry Logic
**File**: `backtesting_utils.py`
```python
@retry(stop=stop_after_attempt(5))  # Number of retry attempts
```

## Extension Points

### Adding New Features

**New UI Element**:
- Add to `dashboard_layout.py`
- Create corresponding callback in `dashboard_callbacks.py`

**New Export Format**:
- Add function to `portfolio_io.py`
- Create callback in `dashboard_callbacks.py`

**New Metric**:
- Add calculation to `calculate_additional_metrics()`
- Update `create_metrics_table()`

**New Data Source**:
- Extend `backtesting_utils.py`
- Maintain same interface

## Performance Considerations

### Caching Strategy
- Portfolio cache: 5 most recent (configurable)
- Auto-cleanup of old cache files
- JSON format for fast serialization

### Data Fetching
- Retry logic with exponential backoff
- 30-second timeout per request
- Individual ticker downloads (parallel-friendly)

### UI Responsiveness
- Debounced weight inputs
- Loading indicators
- Async backtest execution

## Security Considerations

### Input Validation
- Ticker symbols sanitized (uppercase, stripped)
- Weight percentages validated (0-100)
- Total allocation checked (must sum to 100%)
- CSV format validated before parsing

### File Operations
- Only CSV files accepted
- File size limits (handled by browser)
- No arbitrary code execution
- Safe file encoding (UTF-8)

## Future Enhancement Ideas

### Potential Additions
1. Multiple benchmark comparison
2. Monte Carlo simulation
3. Optimization algorithms
4. Risk parity strategies
5. Rebalancing strategies
6. Tax-aware analysis
7. Transaction cost modeling
8. Custom date ranges per ticker
9. Sector allocation analysis
10. Currency hedging options

### Technical Improvements
1. Unit test suite
2. Integration tests
3. CI/CD pipeline
4. Docker containerization
5. Database backend
6. API endpoints
7. Multi-user support
8. Cloud deployment

## Maintenance Guidelines

### Regular Tasks
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Clear cache: Delete `portfolio_cache/` folder
- Review logs: Check `dashboard_debug.log`
- Test imports: Run with various CSV formats

### Code Quality
- Keep functions under 50 lines
- Maintain consistent naming
- Document complex logic
- Add type hints where helpful
- Follow PEP 8 style guide

### Documentation
- Update README when adding features
- Document new export formats
- Add examples for new capabilities
- Keep structure docs current

---

**Last Updated**: 2025-10-25

