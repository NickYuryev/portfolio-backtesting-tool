import argparse
import json
import os
import logging
from datetime import datetime
from backtesting_utils import safe_portfolio_backtest, get_company_name

# Configure logging for cli_dashboard.py to show debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

os.environ['MPLCONFIGDIR'] = '/tmp/.matplotlib'

def run_cli_backtest(tickers_str, allocations_str, benchmark, start_date=None):
    """Run a backtest from CLI inputs and print results."""
    tickers = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    allocations = [float(a.strip()) / 100.0 for a in allocations_str.split(',') if a.strip()]

    if len(tickers) != len(allocations):
        print("Error: Number of tickers and allocations must match.")
        return

    # Fetch company names for display
    company_names = {ticker: get_company_name(ticker) for ticker in tickers}

    results, error_message, warning_message = safe_portfolio_backtest(tickers, allocations, benchmark, start_date)

    if error_message:
        print(f"Backtest Error: {error_message}")
    elif results:
        if warning_message:
            print(f"Warning: {warning_message}")
        print("\n--- Backtest Results ---")
        print(f"Portfolio: {json.dumps({t: f'{w*100:.2f}%' for t, w in zip(tickers, allocations)})}")
        print(f"Company Names: {json.dumps(company_names)}")
        print(f"Benchmark: {benchmark}")
        print(f"Start Date: {start_date if start_date else 'Default (5 years ago)'}")
        print("\nPerformance Statistics:")
        print(results.stats.to_string())

        # Optional: Print prices or other details
        # print("\nPrices:")
        # print(results.prices.head())
    else:
        print("An unknown error occurred during backtesting.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a portfolio backtest from the command line.')
    parser.add_argument('--tickers', type=str, required=True,
                        help='Comma-separated list of stock tickers (e.g., AAPL,GOOGL)')
    parser.add_argument('--allocations', type=str, required=True,
                        help='Comma-separated list of allocation percentages (e.g., 60,40)')
    parser.add_argument('--benchmark', type=str, default='SPY',
                        help='Benchmark ticker (default: SPY)')
    parser.add_argument('--start_date', type=str,
                        help='Start date for backtest (YYYY-MM-DD, default: 5 years ago)')

    args = parser.parse_args()

    run_cli_backtest(args.tickers, args.allocations, args.benchmark, args.start_date)
