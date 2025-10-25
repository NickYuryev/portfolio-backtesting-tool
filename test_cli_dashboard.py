import subprocess
import json
import os
from datetime import datetime, timedelta
from backtesting_utils import safe_portfolio_backtest, get_company_name
import matplotlib.pyplot as plt # Explicitly import matplotlib.pyplot

os.environ['MPLCONFIGDIR'] = '/tmp/.matplotlib' # Set MPLCONFIGDIR for test script

def run_cli_command(tickers, allocations, benchmark, start_date=None):
    command = [
        "python", "cli_dashboard.py",
        "--tickers", ",".join(tickers),
        "--allocations", ",".join(map(str, allocations)),
        "--benchmark", benchmark
    ]
    if start_date:
        command.extend(["--start_date", start_date])

    env = os.environ.copy()
    env['MPLCONFIGDIR'] = '/tmp/.matplotlib'

    print(f"\nRunning command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    print("\n--- CLI Output ---")
    print(result.stdout)
    if result.stderr:
        print("--- CLI Error ---")
        print(result.stderr)
    print("------------------")
    return result.stdout, result.stderr

def run_backtest_direct(tickers, allocations, benchmark, start_date=None):
    print(f"\nRunning direct backtest for tickers: {tickers}, allocations: {allocations}, benchmark: {benchmark}, start_date: {start_date}")
    results, error_message, warning_message = safe_portfolio_backtest(tickers, allocations, benchmark, start_date)
    
    if error_message:
        print(f"Direct Backtest Error: {error_message}")
    elif warning_message:
        print(f"Direct Backtest Warning: {warning_message}")
        print("\nPerformance Statistics:")
        print(results.stats.to_string())
    elif results:
        print("Direct Backtest Successful.")
        print("\nPerformance Statistics:")
        print(results.stats.to_string())
    else:
        print("An unknown error occurred during direct backtest.")

def test_edge_cases():
    print("Starting edge case tests for cli_dashboard.py...")

    # Test Case 1: Sufficient data points (recent start date)
    print("\n--- Test Case 1: Sufficient data points (recent start date) ---")
    recent_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d') # Changed to 90 days for sufficient data
    run_backtest_direct(["AAPL"], [1.0], "SPY", start_date=recent_date) # Use 1.0 for direct call

    # Test Case 2: Valid but small portfolio
    print("\n--- Test Case 2: Valid but small portfolio ---")
    run_backtest_direct(["MSFT", "GOOGL"], [0.5, 0.5], "SPY", start_date="2020-01-01") # Use decimals for direct call

    # Test Case 3: Wrong inputs - Mismatched tickers and allocations (this will be caught by CLI)
    print("\n--- Test Case 3: Mismatched tickers and allocations (CLI test) ---")
    run_cli_command(["AAPL", "MSFT"], [100], "SPY")

    # Test Case 4: Invalid ticker
    print("\n--- Test Case 4: Invalid ticker ---")
    run_backtest_direct(["INVALIDTICKER"], [1.0], "SPY", start_date="2020-01-01")

    # Test Case 5: Allocations not summing to 100% (this will be caught by safe_portfolio_backtest)
    print("\n--- Test Case 5: Allocations not summing to 100% ---")
    run_backtest_direct(["AAPL", "MSFT"], [0.6, 0.3], "SPY", start_date="2020-01-01")

    # Test Case 6: Empty tickers
    print("\n--- Test Case 6: Empty tickers ---")
    run_backtest_direct([], [], "SPY", start_date="2020-01-01")

    # Test Case 7: Future date
    print("\n--- Test Case 7: Future date ---")
    future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    run_backtest_direct(["AAPL"], [1.0], "SPY", start_date=future_date)

    # Test Case 8: Large number of tickers
    print("\n--- Test Case 8: Large number of tickers ---")
    large_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'JPM', 'V', 'MA', 'PG', 
        'HD', 'UNH', 'KO', 'PEP', 'DIS', 'NFLX', 'ADBE', 'CRM', 'PYPL', 'INTC',
        'CMCSA', 'CSCO', 'XOM', 'CVX', 'PFE', 'JNJ', 'MRK', 'ABBV', 'LLY', 'NVO',
        'AZN', 'BABA', 'RY', 'TD', 'BNS', 'BMO', 'CM', 'ENB', 'TRP', 'SU', 
        'CP', 'CNR', 'SHOP', 'LULU', 'CRWD', 'ZM', 'SNOW', 'DDOG', 'FSLY', 'OKTA',
        'TEAM', 'DOCU', 'ZS', 'NET', 'CRSP', 'EDIT', 'BEAM', 'PACB', 'ILMN', 'TWST',
        'MRNA', 'BNTX', 'VIR', 'VRTX', 'GILD', 'REGN', 'AMGN', 'BIIB', 'INCY', 'EXAS',
        'GLD', 'SLV', 'USO', 'BND', 'TLT', 'QQQ', 'SPY', 'DIA', 'IWM', 'EEM',
        'FXI', 'EWJ', 'EWG', 'EZU', 'FM', 'SPG', 'PLD', 'EQIX', 'AMT', 'CCI',
        'PSA', 'DLR', 'O', 'VNQ', 'XLRE', 'KRE', 'XLF', 'SMH', 'SOXX', 'XSD',
        'IGV', 'ARKK', 'QQQM', 'VGT', 'XLK', 'VCR', 'VDC', 'VHT', 'VPU', 'XLY',
        'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLRE', 'XLC', 'XLU', 'XLP', 
        'XLI', 'XLB', 'XLU', 'XLE', 'XLY', 'XLP', 'XLI', 'XLB', 'XLC', 'XLU' 
    ]
    num_large_tickers = len(large_tickers)
    allocations_large = [1.0 / num_large_tickers] * num_large_tickers # Use decimals for direct call
    
    run_backtest_direct(large_tickers, allocations_large, "SPY", start_date="2020-01-01")

    # Test Case 9: Mixed asset types (equities, commodities, bonds/ETFs)
    print("\n--- Test Case 9: Mixed asset types ---")
    mixed_assets = ["AAPL", "GLD", "BND", "USO"]
    allocations_mixed = [0.25, 0.25, 0.25, 0.25]
    run_backtest_direct(mixed_assets, allocations_mixed, "SPY", start_date="2015-01-01")

    # Test Case 10: Tickers with sparse or very short history (e.g., new IPOs, delisted, or very illiquid)
    print("\n--- Test Case 10: Tickers with sparse/short history ---")
    sparse_tickers = ["GME", "AMC", "DISH"]
    allocations_sparse = [0.3333, 0.3333, 0.3334]
    run_backtest_direct(sparse_tickers, allocations_sparse, "SPY", start_date="2023-01-01")

    print("\nEdge case tests complete.")

if __name__ == '__main__':
    test_edge_cases()
