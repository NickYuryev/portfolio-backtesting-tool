"""
Portfolio Backtesting Dashboard - Main Application
A comprehensive tool for backtesting portfolio allocations using yfinance data
"""

import dash
import logging
from dashboard_layout import create_layout
from dashboard_utils import initialize_cache_dir
import dashboard_callbacks

# Set up logging
logging.basicConfig(
    filename='dashboard_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Initialize cache directory
initialize_cache_dir()

# Set layout
app.layout = create_layout()

# Register all callbacks
dashboard_callbacks.register_callbacks(app)

if __name__ == '__main__':
    logger.info("Starting Portfolio Backtesting Dashboard")
    app.run(debug=False, host='127.0.0.1', port=8050)

