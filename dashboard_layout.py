"""
Dashboard Layout Module
Defines the UI layout for the portfolio backtesting dashboard
"""

from dash import dcc, html
import json


def create_layout():
    """Create and return the main dashboard layout"""
    return html.Div([
        # Hidden divs to store state
        html.Div(id='portfolio-data', style={'display': 'none'}),
        html.Div(id='company-names', style={'display': 'none'}),
        html.Div(id='log-returns-mode', children=json.dumps(False), style={'display': 'none'}),
        dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),
        
        # Download component for export
        dcc.Download(id='download-portfolio'),
        
        html.Div([
            html.H1('Portfolio Backtesting Dashboard', 
                    style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
            
            # Main container with two columns
            html.Div([
                # Left column - Portfolio Builder
                create_portfolio_builder(),
                
                # Right column - Results
                create_results_panel()
                
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
        ], style={'padding': '40px', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})
    ])


def create_portfolio_builder():
    """Create the left column portfolio builder panel"""
    return html.Div([
        html.H3('Portfolio Builder', style={'color': '#34495e', 'marginBottom': '20px'}),
        
        # Load saved portfolio section
        html.Div([
            html.Label('Load Saved Portfolio:', style={'marginRight': '10px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='saved-portfolios-dropdown',
                placeholder='Select a saved portfolio...',
                style={'marginBottom': '20px'}
            ),
        ], style={'marginBottom': '20px'}),
        
        # Import/Export section
        html.Div([
            html.Label('Import/Export:', style={'marginRight': '10px', 'fontWeight': 'bold'}),
            html.Div([
                dcc.Upload(
                    id='upload-portfolio',
                    children=html.Button('📁 Import CSV', 
                                       style={
                                           'backgroundColor': '#9b59b6',
                                           'color': 'white',
                                           'border': 'none',
                                           'padding': '8px 16px',
                                           'cursor': 'pointer',
                                           'borderRadius': '5px',
                                           'marginRight': '10px',
                                           'fontSize': '14px'
                                       }),
                    multiple=False
                ),
                html.Button('💾 Export CSV', 
                           id='export-button',
                           n_clicks=0,
                           style={
                               'backgroundColor': '#16a085',
                               'color': 'white',
                               'border': 'none',
                               'padding': '8px 16px',
                               'cursor': 'pointer',
                               'borderRadius': '5px',
                               'marginRight': '10px',
                               'fontSize': '14px'
                           }),
                html.A('📋 Sample CSV',
                       id='download-sample-link',
                       download='portfolio_template.csv',
                       href='',
                       style={
                           'backgroundColor': '#95a5a6',
                           'color': 'white',
                           'border': 'none',
                           'padding': '8px 16px',
                           'cursor': 'pointer',
                           'borderRadius': '5px',
                           'textDecoration': 'none',
                           'fontSize': '14px',
                           'display': 'inline-block'
                       })
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '5px'})
        ], style={'marginBottom': '20px', 'padding': '15px', 'backgroundColor': '#ffffff', 'borderRadius': '5px'}),
        
        # Import/Export status message
        html.Div(id='import-export-status', style={'marginBottom': '15px', 'fontSize': '12px'}),
        
        # Add ticker section
        html.Div([
            dcc.Input(
                id='new-ticker-input',
                type='text',
                placeholder='Enter ticker (e.g., AAPL)',
                style={'marginRight': '10px', 'padding': '10px', 'width': '200px'}
            ),
            html.Button('+ Add Holding', id='add-ticker-button', n_clicks=0,
                       style={
                           'backgroundColor': '#3498db',
                           'color': 'white',
                           'border': 'none',
                           'padding': '10px 20px',
                           'cursor': 'pointer',
                           'borderRadius': '5px'
                       })
        ], style={'marginBottom': '20px'}),
        
        # Portfolio holdings table
        html.Div(id='portfolio-container', children=[]),
        
        # Total allocation display
        html.Div(id='total-allocation', style={'marginTop': '20px', 'fontSize': '16px'}),
        
        # Save status
        html.Div(id='save-status', style={'marginTop': '10px', 'fontSize': '12px', 'color': '#27ae60'}),
        
        # Benchmark and date inputs
        html.Div([
            html.H3('Benchmark & Settings', style={'color': '#34495e', 'marginTop': '30px', 'marginBottom': '20px'}),
            dcc.Input(
                id='benchmark-input',
                type='text',
                placeholder='Benchmark ticker (e.g., SPY)',
                value='SPY',
                style={'marginBottom': '10px', 'padding': '10px', 'width': '100%'}
            ),
            dcc.Input(
                id='start-date-input',
                type='text',
                placeholder='Start Date (YYYY-MM-DD, leave blank for latest common date)',
                style={'marginBottom': '10px', 'padding': '10px', 'width': '100%'}
            ),
            html.Button('Run Backtest', id='run-button', n_clicks=0,
                       style={
                           'backgroundColor': '#27ae60',
                           'color': 'white',
                           'border': 'none',
                           'padding': '15px 30px',
                           'cursor': 'pointer',
                           'borderRadius': '5px',
                           'width': '100%',
                           'fontSize': '16px',
                           'marginTop': '10px'
                       })
        ])
    ], style={'width': '35%', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'})


def create_results_panel():
    """Create the right column results panel"""
    return html.Div([
        # Log Scale Toggle
        html.Div([
            html.Button('Toggle Log Scale', id='toggle-log-returns-button', n_clicks=0,
                        style={
                            'backgroundColor': '#3498db',
                            'color': 'white',
                            'border': 'none',
                            'padding': '10px 20px',
                            'cursor': 'pointer',
                            'borderRadius': '5px',
                            'marginRight': '10px'
                        }),
            html.Div(id='log-returns-status', style={'display': 'inline-block', 'verticalAlign': 'middle'})
        ], style={'textAlign': 'center', 'marginTop': '20px', 'marginBottom': '20px'}),
        
        # Export Metrics Button
        html.Div([
            html.Button('📊 Export Full Report (Metrics + Data)', 
                       id='export-metrics-button',
                       n_clicks=0,
                       style={
                           'backgroundColor': '#e67e22',
                           'color': 'white',
                           'border': 'none',
                           'padding': '10px 20px',
                           'cursor': 'pointer',
                           'borderRadius': '5px'
                       }),
            dcc.Download(id='download-metrics')
        ], style={'textAlign': 'center', 'marginBottom': '20px'}),
        
        # Results display
        dcc.Loading(
            id="loading-results",
            children=[html.Div(id='backtest-results', style={'overflowX': 'auto', 'width': '100%'})],
            type="default"
        )
    ], style={'width': '60%', 'marginLeft': '5%'})

