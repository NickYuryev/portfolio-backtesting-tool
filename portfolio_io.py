"""
Portfolio Import/Export Module
Handles CSV import/export for portfolio allocations and metrics
"""

import pandas as pd
import json
import base64
import io
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def portfolio_to_csv(portfolio: Dict[str, float], company_names: Dict[str, str]) -> str:
    """
    Convert portfolio to CSV string
    
    Args:
        portfolio: Dictionary of {ticker: weight}
        company_names: Dictionary of {ticker: company_name}
        
    Returns:
        CSV string with columns: Ticker, Company Name, Weight (%)
    """
    data = []
    for ticker, weight in portfolio.items():
        data.append({
            'Ticker': ticker,
            'Company Name': company_names.get(ticker, 'N/A'),
            'Weight (%)': round(weight * 100, 2)
        })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def csv_to_portfolio(csv_content: str) -> Tuple[Optional[Dict[str, float]], Optional[Dict[str, str]], Optional[str]]:
    """
    Parse CSV content and return portfolio and company names
    
    Args:
        csv_content: CSV string content
        
    Returns:
        Tuple of (portfolio_dict, company_names_dict, error_message)
        Returns (None, None, error_msg) if parsing fails
    """
    try:
        # Read CSV
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Validate required columns
        required_cols = ['Ticker', 'Weight (%)']
        if not all(col in df.columns for col in required_cols):
            return None, None, f"CSV must contain columns: {', '.join(required_cols)}"
        
        # Check for empty data
        if df.empty:
            return None, None, "CSV file is empty"
        
        portfolio = {}
        company_names = {}
        
        for _, row in df.iterrows():
            ticker = str(row['Ticker']).strip().upper()
            
            # Skip empty rows
            if not ticker or ticker == 'NAN':
                continue
            
            # Parse weight
            try:
                weight = float(row['Weight (%)']) / 100.0
                if weight < 0 or weight > 1:
                    return None, None, f"Weight for {ticker} must be between 0 and 100%"
                portfolio[ticker] = weight
            except (ValueError, TypeError):
                return None, None, f"Invalid weight value for {ticker}: {row['Weight (%)']}"
            
            # Get company name if available
            if 'Company Name' in df.columns:
                company_name = str(row['Company Name'])
                if company_name and company_name != 'nan' and company_name != 'N/A':
                    company_names[ticker] = company_name
        
        if not portfolio:
            return None, None, "No valid ticker data found in CSV"
        
        # Validate total allocation
        total_weight = sum(portfolio.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Total portfolio weight is {total_weight*100:.2f}%, not 100%")
            # Don't return error, just log warning - user can adjust
        
        return portfolio, company_names, None
        
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        return None, None, f"Error parsing CSV: {str(e)}"


def parse_upload_content(contents: str, filename: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse uploaded file content from Dash Upload component
    
    Args:
        contents: Base64 encoded file content from dcc.Upload
        filename: Name of uploaded file
        
    Returns:
        Tuple of (decoded_content, error_message)
    """
    try:
        # Check file extension
        if not filename.lower().endswith('.csv'):
            return None, "Please upload a CSV file"
        
        # Decode base64 content
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        decoded_str = decoded.decode('utf-8')
        
        return decoded_str, None
        
    except Exception as e:
        logger.error(f"Error decoding upload: {e}")
        return None, f"Error reading file: {str(e)}"


def create_sample_csv() -> str:
    """
    Create a sample CSV template for portfolio import
    
    Returns:
        CSV string with sample data
    """
    sample_data = [
        {'Ticker': 'AAPL', 'Company Name': 'Apple Inc.', 'Weight (%)': 30.0},
        {'Ticker': 'GOOGL', 'Company Name': 'Alphabet Inc.', 'Weight (%)': 25.0},
        {'Ticker': 'MSFT', 'Company Name': 'Microsoft Corporation', 'Weight (%)': 25.0},
        {'Ticker': 'AMZN', 'Company Name': 'Amazon.com Inc.', 'Weight (%)': 20.0},
    ]
    df = pd.DataFrame(sample_data)
    return df.to_csv(index=False)


def create_comprehensive_metrics_csv(results, calculated_metrics: Dict, benchmark: str) -> str:
    """
    Create comprehensive CSV export with performance data and metrics
    
    Args:
        results: Backtest results object
        calculated_metrics: Dictionary of calculated metrics
        benchmark: Benchmark ticker symbol
        
    Returns:
        CSV string with multiple sections
    """
    output = io.StringIO()
    
    # Section 1: Portfolio Performance Time Series
    output.write("PORTFOLIO PERFORMANCE TIME SERIES\n")
    output.write(f"Data shows portfolio value normalized to 100 at start\n\n")
    
    portfolio_prices = results.prices['Portfolio']
    benchmark_prices = results.prices['Benchmark']
    
    # Normalize to base 100
    portfolio_normalized = (portfolio_prices / portfolio_prices.iloc[0]) * 100
    benchmark_normalized = (benchmark_prices / benchmark_prices.iloc[0]) * 100
    
    performance_df = pd.DataFrame({
        'Date': portfolio_normalized.index.strftime('%Y-%m-%d'),
        'Portfolio Value (Base=100)': portfolio_normalized.values,
        f'Benchmark {benchmark} (Base=100)': benchmark_normalized.values
    })
    performance_df.to_csv(output, index=False)
    
    # Section 2: Key Performance Metrics
    output.write("\n\nKEY PERFORMANCE METRICS\n\n")
    
    metrics_data = [
        {'Metric': 'Annualized Return', 
         'Portfolio': f"{calculated_metrics['portfolio_ann_return']*100:.2f}%",
         'Benchmark': f"{calculated_metrics['benchmark_ann_return']*100:.2f}%"},
        {'Metric': 'Relative Return (vs Benchmark)', 
         'Portfolio': f"{calculated_metrics['relative_ann_return']*100:+.2f}%",
         'Benchmark': '—'},
        {'Metric': 'Volatility (Std Dev)', 
         'Portfolio': f"{calculated_metrics['portfolio_std']*100:.2f}%",
         'Benchmark': f"{calculated_metrics['benchmark_std']*100:.2f}%"},
        {'Metric': 'Correlation with Benchmark', 
         'Portfolio': f"{calculated_metrics['correlation']:.4f}" if isinstance(calculated_metrics['correlation'], (int, float)) else 'N/A',
         'Benchmark': '1.0000'},
        {'Metric': 'Best Year', 
         'Portfolio': f"{calculated_metrics['best_year']:.2f}%" if isinstance(calculated_metrics['best_year'], (int, float)) else 'N/A',
         'Benchmark': f"{calculated_metrics['benchmark_best']:.2f}%" if isinstance(calculated_metrics['benchmark_best'], (int, float)) else 'N/A'},
        {'Metric': 'Worst Year', 
         'Portfolio': f"{calculated_metrics['worst_year']:.2f}%" if isinstance(calculated_metrics['worst_year'], (int, float)) else 'N/A',
         'Benchmark': f"{calculated_metrics['benchmark_worst']:.2f}%" if isinstance(calculated_metrics['benchmark_worst'], (int, float)) else 'N/A'},
    ]
    
    metrics_df = pd.DataFrame(metrics_data)
    metrics_df.to_csv(output, index=False)
    
    # Section 3: Detailed Statistics
    output.write("\n\nDETAILED STATISTICS\n\n")
    
    stats = results.stats
    stats_df = pd.DataFrame({
        'Metric': stats.index,
        'Portfolio': stats['Portfolio'].values,
        'Benchmark': stats['Benchmark'].values
    })
    stats_df.to_csv(output, index=False)
    
    return output.getvalue()

