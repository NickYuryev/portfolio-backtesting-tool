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
            "💼 No holdings yet. Add a ticker to get started.",
            style={
                'textAlign': 'center',
                'color': '#9ca3af',
                'padding': '40px 20px',
                'backgroundColor': '#f9fafb',
                'borderRadius': '12px',
                'fontSize': '15px'
            }
        )
    
    table_rows = []
    for i, (ticker, weight) in enumerate(portfolio.items()):
        company_name = company_names.get(ticker, 'Loading...')
        row_style = {
            'backgroundColor': '#ffffff' if i % 2 == 0 else '#f9fafb'
        }
        
        table_rows.append(
            html.Tr([
                html.Td(ticker, style={
                    'padding': '16px',
                    'fontWeight': '700',
                    'color': '#1f2937',
                    'fontSize': '14px'
                }),
                html.Td(company_name, style={
                    'padding': '16px',
                    'fontSize': '13px',
                    'color': '#6b7280'
                }),
                html.Td([
                    dcc.Input(
                        id={'type': 'weight-input', 'index': ticker},
                        type='number',
                        value=round(weight * 100, 2),
                        min=0,
                        max=100,
                        step=0.01,
                        style={
                            'width': '90px',
                            'marginRight': '8px',
                            'padding': '8px 12px',
                            'border': '2px solid #e5e7eb',
                            'borderRadius': '6px',
                            'fontSize': '14px'
                        },
                        debounce=True
                    ),
                    html.Span('%', style={'color': '#6b7280', 'fontSize': '14px'})
                ], style={'padding': '16px'}),
                html.Td([
                    html.Button('×', 
                               id={'type': 'remove-button', 'index': ticker},
                               n_clicks=0,
                               style={
                                   'backgroundColor': '#ef4444',
                                   'color': 'white',
                                   'border': 'none',
                                   'padding': '6px 12px',
                                   'cursor': 'pointer',
                                   'borderRadius': '6px',
                                   'fontSize': '18px',
                                   'fontWeight': 'bold',
                                   'transition': 'all 0.2s',
                                   'boxShadow': '0 2px 4px rgba(239, 68, 68, 0.3)'
                               })
                ], style={'padding': '16px', 'textAlign': 'center'})
            ], style=row_style)
        )
    
    return html.Div([
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th('Ticker', style={
                        'padding': '14px 16px',
                        'background': '#023047',
                        'color': 'white',
                        'fontWeight': '600',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px',
                        'textAlign': 'left'
                    }),
                    html.Th('Company Name', style={
                        'padding': '14px 16px',
                        'background': '#023047',
                        'color': 'white',
                        'fontWeight': '600',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px',
                        'textAlign': 'left'
                    }),
                    html.Th('Weight (%)', style={
                        'padding': '14px 16px',
                        'background': '#023047',
                        'color': 'white',
                        'fontWeight': '600',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px',
                        'textAlign': 'left'
                    }),
                    html.Th('Action', style={
                        'padding': '14px 16px',
                        'background': '#023047',
                        'color': 'white',
                        'fontWeight': '600',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px',
                        'textAlign': 'center'
                    })
                ])
            ]),
            html.Tbody(table_rows)
        ], style={
            'width': '100%',
            'borderCollapse': 'separate',
            'borderSpacing': '0'
        })
    ], style={
        'backgroundColor': 'white',
        'borderRadius': '12px',
        'overflow': 'hidden',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
        'marginTop': '15px'
    })


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
    
    # Color coding with tolerance for floating point errors
    if abs(total - 100) < 0.01:
        bg_color = '#d1fae5'
        text_color = '#065f46'
        icon = '✓'
        border_color = '#10b981'
    elif total < 100:
        bg_color = '#fef3c7'
        text_color = '#92400e'
        icon = '⚠️'
        border_color = '#f59e0b'
    else:
        bg_color = '#fee2e2'
        text_color = '#991b1b'
        icon = '❌'
        border_color = '#ef4444'
    
    return html.Div([
        html.Span(icon, style={'marginRight': '8px', 'fontSize': '16px'}),
        html.Span(f"Total Allocation: ", style={'fontWeight': '600'}),
        html.Span(f"{total:.2f}%", style={'fontWeight': '700'})
    ], style={
        'color': text_color,
        'backgroundColor': bg_color,
        'padding': '12px 20px',
        'borderRadius': '10px',
        'border': f'2px solid {border_color}',
        'fontSize': '15px',
        'display': 'inline-block',
        'boxShadow': f'0 2px 4px {border_color}40'
    })

