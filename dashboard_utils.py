"""
Dashboard Utility Functions
Helper functions for caching, formatting, and logging
"""

import json
import os
import glob
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

# Cache directory configuration
CACHE_DIR = 'portfolio_cache'


def initialize_cache_dir():
    """Create cache directory if it doesn't exist"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def save_portfolio_to_cache(portfolio: Dict[str, float], company_names: Dict[str, str]):
    """
    Save portfolio to cache with timestamp
    
    Args:
        portfolio: Dictionary of {ticker: weight}
        company_names: Dictionary of {ticker: company_name}
    """
    initialize_cache_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(CACHE_DIR, f'portfolio_{timestamp}.json')
    
    cache_data = {
        'portfolio': portfolio,
        'company_names': company_names,
        'timestamp': timestamp,
        'saved_at': datetime.now().isoformat()
    }
    
    with open(filename, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    # Clean up old cache files (keep only 5 most recent)
    cache_files = sorted(glob.glob(os.path.join(CACHE_DIR, 'portfolio_*.json')))
    if len(cache_files) > 5:
        for old_file in cache_files[:-5]:
            try:
                os.remove(old_file)
            except Exception as e:
                logger.warning(f"Could not remove old cache file {old_file}: {e}")


def load_cached_portfolios() -> List[Dict]:
    """
    Load all cached portfolios
    
    Returns:
        List of cached portfolio dictionaries
    """
    initialize_cache_dir()
    cache_files = sorted(glob.glob(os.path.join(CACHE_DIR, 'portfolio_*.json')), reverse=True)
    portfolios = []
    
    for file_path in cache_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                data['file_path'] = file_path
                portfolios.append(data)
        except Exception as e:
            logger.warning(f"Could not load cache file {file_path}: {e}")
    
    return portfolios


def format_portfolio_label(cache_data: Dict) -> str:
    """
    Format portfolio label for dropdown display
    
    Args:
        cache_data: Cached portfolio data dictionary
        
    Returns:
        Formatted label string
    """
    saved_at = datetime.fromisoformat(cache_data['saved_at'])
    portfolio = cache_data['portfolio']
    tickers = list(portfolio.keys())[:3]
    ticker_str = ', '.join(tickers)
    if len(portfolio) > 3:
        ticker_str += f' +{len(portfolio) - 3} more'
    
    return f"{saved_at.strftime('%Y-%m-%d %H:%M')} - {ticker_str}"


def log_event(msg: str, **kwargs):
    """
    Log event with structured key-value pairs
    
    Args:
        msg: Main message
        **kwargs: Additional key-value pairs to log
    """
    log_msg = f"{msg} | " + ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(log_msg)
    print(log_msg)


def create_portfolio_table_html(portfolio: Dict[str, float], company_names: Dict[str, str]):
    """
    Create HTML table for portfolio display
    
    Args:
        portfolio: Dictionary of {ticker: weight}
        company_names: Dictionary of {ticker: company_name}
        
    Returns:
        Dash HTML table component
    """
    from dash import html, dcc
    
    if not portfolio:
        return html.Div(
            "No holdings yet. Add a ticker to get started.",
            style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '20px'}
        )
    
    table_rows = []
    for ticker, weight in portfolio.items():
        company_name = company_names.get(ticker, 'Loading...')
        
        table_rows.append(
            html.Tr([
                html.Td(ticker, style={'padding': '10px', 'fontWeight': 'bold'}),
                html.Td(company_name, style={'padding': '10px', 'fontSize': '12px', 'color': '#555'}),
                html.Td([
                    dcc.Input(
                        id={'type': 'weight-input', 'index': ticker},
                        type='number',
                        value=round(weight * 100, 2),
                        min=0,
                        max=100,
                        step=0.01,
                        style={'width': '100px', 'marginRight': '5px'},
                        debounce=True
                    ),
                    html.Span('%')
                ], style={'padding': '10px'}),
                html.Td([
                    html.Button('×', 
                               id={'type': 'remove-button', 'index': ticker},
                               n_clicks=0,
                               style={
                                   'backgroundColor': '#e74c3c',
                                   'color': 'white',
                                   'border': 'none',
                                   'padding': '5px 10px',
                                   'cursor': 'pointer',
                                   'borderRadius': '3px',
                                   'fontSize': '18px',
                                   'fontWeight': 'bold'
                               })
                ], style={'padding': '10px'})
            ])
        )
    
    return html.Table([
        html.Thead([
            html.Tr([
                html.Th('Ticker', style={'padding': '10px', 'backgroundColor': '#34495e', 'color': 'white'}),
                html.Th('Company Name', style={'padding': '10px', 'backgroundColor': '#34495e', 'color': 'white'}),
                html.Th('Weight (%)', style={'padding': '10px', 'backgroundColor': '#34495e', 'color': 'white'}),
                html.Th('Action', style={'padding': '10px', 'backgroundColor': '#34495e', 'color': 'white'})
            ])
        ]),
        html.Tbody(table_rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginTop': '10px', 'border': '1px solid #ddd'})


def format_total_allocation(portfolio: Dict[str, float]):
    """
    Format total allocation display with color coding
    
    Args:
        portfolio: Dictionary of {ticker: weight}
        
    Returns:
        Dash HTML div with formatted allocation
    """
    from dash import html
    
    total = sum(portfolio.values()) * 100
    total_text = f"Total Allocation: {total:.2f}%"
    
    # Color coding with tolerance for floating point errors
    if abs(total - 100) < 0.01:
        total_style = {'color': '#27ae60', 'fontWeight': 'bold'}
    elif total < 100:
        total_style = {'color': '#e67e22', 'fontWeight': 'bold'}
    else:
        total_style = {'color': '#e74c3c', 'fontWeight': 'bold'}
    
    return html.Div(total_text, style=total_style)

