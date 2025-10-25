import yfinance as yf
import bt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, \
                    retry_if_exception_type, wait_fixed, before_log, after_log
import logging
import requests # Import requests for Timeout exception

logger = logging.getLogger(__name__)

def get_company_name(ticker):
    """Fetch company name from yfinance"""
    try:
        info = yf.Ticker(ticker).info
        # Try different fields where company name might be stored
        name = info.get('longName') or info.get('shortName') or info.get('symbol')
        if name is None:
            # Fallback to ticker itself if no name is found
            name = ticker
        # Truncate if too long
        if len(name) > 30:
            name = name[:27] + '...'
        return name
    except Exception as e:
        logger.warning(f"Error fetching company name for {ticker}: {e}") # Log warning
        return 'Name not found'

@retry(stop=stop_after_attempt(5),
       wait=wait_exponential(multiplier=1, min=4, max=10),
       retry=retry_if_exception_type((yf.exceptions.YFPricesMissingError, yf.exceptions.YFTzMissingError, requests.exceptions.Timeout)), # Use specific yfinance and requests exceptions
       before=before_log(logger, logging.DEBUG),
       after=after_log(logger, logging.DEBUG),
       reraise=True)
def _download_data_with_retries(tickers, start_date):
    """Helper function to download data with retries for transient errors."""
    logger.debug(f"Attempting to download data for {tickers} from {start_date}")
    # Increased timeout to 30 seconds for robustness
    data = yf.download(tickers, start=start_date, auto_adjust=True, progress=False, timeout=30)['Close']
    if data.empty:
        raise yf.exceptions.YFPricesMissingError(f"No data returned for {tickers} starting {start_date}") # Raise specific exception
    return data

def safe_portfolio_backtest(tickers, allocations, benchmark, start_date=None):
    """Enhanced portfolio backtest with comprehensive error handling"""
    try:
        # Validate inputs
        if not tickers or not allocations:
            return None, "Portfolio is empty. Please add at least one holding.", None

        if abs(sum(allocations) - 1.0) > 0.01:
            return None, f"Allocations must sum to 100%. Current sum: {sum(allocations)*100:.2f}%", None

        # Set default start date if not provided
        if not start_date:
            # If no start date, find the LATEST start date among all tickers
            # (i.e., the most recent date when the last ticker began trading)
            all_tickers_for_date = tickers + [benchmark]
            start_date = "1900-01-01" # Default to a very early date
            try:
                # Get the history for all tickers to find the latest common start date
                data_for_dates = yf.download(all_tickers_for_date, period="max", auto_adjust=True, progress=False)['Close']
                if not data_for_dates.empty:
                    # Find the latest start date (when the youngest ticker started)
                    # This ensures all tickers have data for the entire backtest period
                    first_valid_dates = data_for_dates.apply(lambda col: col.first_valid_index())
                    start_date = first_valid_dates.max().strftime('%Y-%m-%d')
            except Exception as e:
                # If there's an issue, fall back to the 5-year default.
                logger.warning(f"Could not determine max start date, defaulting to 5 years. Error: {e}")
                start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        
        all_tickers = tickers + [benchmark]
        successful_downloads = []
        failed_downloads = []
        data_frames = []

        for ticker in all_tickers:
            try:
                # Attempt to download each ticker individually with retries
                ticker_data = _download_data_with_retries([ticker], start_date)
                data_frames.append(ticker_data)
                successful_downloads.append(ticker)
            except (yf.exceptions.YFPricesMissingError, yf.exceptions.YFTzMissingError, requests.exceptions.Timeout) as e: # Catch specific exceptions
                failed_downloads.append(f"{ticker}: {str(e)}")
            except Exception as e:
                failed_downloads.append(f"{ticker}: Unexpected error - {str(e)}")

        if not successful_downloads:
            return None, f"Could not download data for any ticker. Failed: {'; '.join(failed_downloads)}", None

        # Combine successful dataframes
        if len(data_frames) > 1:
            data = pd.concat(data_frames, axis=1)
        else:
            # Handle case where only one ticker was successfully downloaded
            data = data_frames[0]
            if isinstance(data, pd.Series):
                data = data.to_frame(name=successful_downloads[0])

        # Filter out tickers that were not successfully downloaded or have all NaNs
        # This also ensures 'data' only contains columns for tickers in 'successful_downloads'
        data = data[successful_downloads].dropna(axis=1, how='all')

        if data.empty:
            return None, "No valid data found after attempting downloads and filtering.", None

        # Check for any tickers that ended up being completely empty after initial download attempts
        final_missing_tickers = [t for t in successful_downloads if t not in data.columns or data[t].isnull().all()]
        if final_missing_tickers:
            return None, f"No valid data found for: {', '.join(final_missing_tickers)} after download attempts. Check ticker symbols or date range.", None

        data = data.ffill().bfill() # Fill any remaining NaNs within valid columns
        data = data.dropna() # Drop rows that are still all NaN if start date is too early for any ticker

        # Separate portfolio tickers and benchmark from the successfully downloaded data
        portfolio_tickers_in_data = [t for t in tickers if t in data.columns]
        benchmark_in_data = benchmark if benchmark in data.columns else None

        if len(data) < 20:
            # Identify which tickers have insufficient data
            insufficient_data_tickers = []
            for ticker in (portfolio_tickers_in_data + [benchmark_in_data]):
                if ticker in data.columns and len(data[ticker].dropna()) < 20:
                    insufficient_data_tickers.append(ticker)
            
            if insufficient_data_tickers:
                return None, f"Insufficient data points (need at least 20 trading days) for: {', '.join(insufficient_data_tickers)}. Please adjust the start date or choose tickers with longer history.", None
            else:
                return None, "Insufficient data points for backtesting (need at least 20 trading days). Please adjust the start date or choose tickers with longer history.", None

        if not portfolio_tickers_in_data:
            return None, "No portfolio tickers found with valid data to perform backtest.", None
        
        # If benchmark failed to download, provide a specific error or proceed without it (for now, error)
        if not benchmark_in_data:
            return None, f"Benchmark ticker '{benchmark}' not found or has no valid data. Failed downloads: {'; '.join(failed_downloads)}", None

        # Create strategies using only available tickers
        allocations_dict = {t: alloc for t, alloc in zip(tickers, allocations) if t in portfolio_tickers_in_data}

        # Normalize allocations if some tickers were removed
        current_total_allocation = sum(allocations_dict.values())
        if current_total_allocation == 0:
             return None, "All portfolio tickers removed or zero allocation after data filtering.", None
        
        if abs(current_total_allocation - 1.0) > 0.01: # Only normalize if it deviates significantly from 1
             normalized_factor = 1.0 / current_total_allocation
             allocations_dict = {k: v * normalized_factor for k, v in allocations_dict.items()}

        portfolio_strategy = bt.Strategy('Portfolio', [
            bt.algos.RunOnce(),
            bt.algos.SelectAll(), # Select all available tickers in the data
            bt.algos.WeighSpecified(**allocations_dict),
            bt.algos.Rebalance()
        ])
        
        benchmark_strategy = bt.Strategy('Benchmark', [
            bt.algos.RunOnce(),
            bt.algos.SelectAll(),
            bt.algos.WeighEqually(),
            bt.algos.Rebalance()
        ])
        
        # Run backtests with potentially filtered data
        portfolio_backtest = bt.Backtest(portfolio_strategy, data[portfolio_tickers_in_data].copy())
        benchmark_backtest = bt.Backtest(benchmark_strategy, data[[benchmark_in_data]].copy())
        results = bt.run(portfolio_backtest, benchmark_backtest)
        
        # Include information about failed downloads in the success message if any
        if failed_downloads:
            warning_message = f"Backtest completed with some data issues. Failed downloads: {'; '.join(failed_downloads)}"
            return results, None, warning_message # Return error as None, warning message
        
        return results, None, None # No error, no warning
        
    except Exception as e:
        return None, f"Unexpected error during backtest: {str(e)}", None
