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
        html.Div(id='dark-mode', children=json.dumps(False), style={'display': 'none'}),
        dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),
        
        # Download component for export
        dcc.Download(id='download-portfolio'),
        
        html.Div(id='main-container', children=[
            # Header with professional blue background
            html.Div([
                html.Div([
                    html.H1('📊 Portfolio Backtesting Dashboard', 
                            style={
                                'textAlign': 'center', 
                                'color': 'white',
                                'marginBottom': '0',
                                'fontSize': '42px',
                                'fontWeight': '700',
                                'letterSpacing': '-0.5px',
                                'textShadow': '0 2px 4px rgba(0,0,0,0.2)'
                            }),
                    html.P('Professional-grade portfolio analysis and performance metrics',
                           style={
                               'textAlign': 'center',
                               'color': 'rgba(255,255,255,0.95)',
                               'fontSize': '16px',
                               'marginTop': '10px',
                               'marginBottom': '0'
                           })
                ], style={'flex': '1'}),
                html.Button('🌙 Dark Mode', 
                           id='dark-mode-toggle',
                           n_clicks=0,
                           style={
                               'position': 'absolute',
                               'top': '20px',
                               'right': '30px',
                               'backgroundColor': 'rgba(255,255,255,0.15)',
                               'color': 'white',
                               'border': '2px solid rgba(255,255,255,0.3)',
                               'padding': '10px 20px',
                               'cursor': 'pointer',
                               'borderRadius': '8px',
                               'fontSize': '14px',
                               'fontWeight': '600',
                               'transition': 'all 0.3s',
                               'backdropFilter': 'blur(10px)'
                           })
            ], style={
                'background': '#023047',
                'padding': '40px 20px',
                'marginBottom': '40px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'position': 'relative',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            }),
            
            # Main container with two columns
            html.Div([
                html.Div([
                    # Left column - Portfolio Builder
                    create_portfolio_builder(),
                    
                    # Right column - Results
                    create_results_panel()
                    
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'gap': '30px',
                    'maxWidth': '1600px',
                    'margin': '0 auto'
                })
            ], style={'padding': '0 40px 40px 40px'})
        ], style={
            'padding': '0',
            'backgroundColor': '#f0f2f5',
            'minHeight': '100vh',
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            'transition': 'all 0.3s ease'
        })
    ], id='app-container')


def create_portfolio_builder():
    """Create the left column portfolio builder panel"""
    return html.Div(id='portfolio-builder-panel', children=[
        html.H3('🎯 Portfolio Builder', 
                style={
                    'color': '#2d3748',
                    'marginBottom': '25px',
                    'fontSize': '24px',
                    'fontWeight': '600'
                }),
        
        # Load saved portfolio section
        html.Div(className='theme-card', children=[
            html.Label('📂 Load Saved Portfolio', 
                      className='theme-label',
                      style={
                          'marginBottom': '10px',
                          'fontWeight': '600',
                          'fontSize': '14px',
                          'display': 'block'
                      }),
            dcc.Dropdown(
                id='saved-portfolios-dropdown',
                placeholder='Select a saved portfolio...',
                style={
                    'marginBottom': '0',
                    'borderRadius': '8px',
                    'fontSize': '14px'
                }
            ),
        ], style={
            'marginBottom': '25px',
            'padding': '20px',
            'borderRadius': '12px',
            'transition': 'all 0.3s ease'
        }),
        
        # Import/Export section
        html.Div(className='theme-card', children=[
            html.Label('📤 Import/Export', 
                      className='theme-label',
                      style={
                          'marginBottom': '15px',
                          'fontWeight': '600',
                          'fontSize': '14px',
                          'display': 'block'
                      }),
            html.Div([
                dcc.Upload(
                    id='upload-portfolio',
                    children=html.Button('📁 Import CSV', 
                                       style={
                                           'backgroundColor': '#8b5cf6',
                                           'color': 'white',
                                           'border': 'none',
                                           'padding': '10px 20px',
                                           'cursor': 'pointer',
                                           'borderRadius': '8px',
                                           'fontSize': '14px',
                                           'fontWeight': '500',
                                           'transition': 'all 0.2s',
                                           'boxShadow': '0 2px 4px rgba(139, 92, 246, 0.3)'
                                       }),
                    multiple=False
                ),
                html.Button('💾 Export CSV', 
                           id='export-button',
                           n_clicks=0,
                           style={
                               'backgroundColor': '#10b981',
                               'color': 'white',
                               'border': 'none',
                               'padding': '10px 20px',
                               'cursor': 'pointer',
                               'borderRadius': '8px',
                               'fontSize': '14px',
                               'fontWeight': '500',
                               'transition': 'all 0.2s',
                               'boxShadow': '0 2px 4px rgba(16, 185, 129, 0.3)'
                           }),
                html.A('📋 Sample CSV',
                       id='download-sample-link',
                       download='portfolio_template.csv',
                       href='',
                       style={
                           'backgroundColor': '#6b7280',
                           'color': 'white',
                           'border': 'none',
                           'padding': '10px 20px',
                           'cursor': 'pointer',
                           'borderRadius': '8px',
                           'textDecoration': 'none',
                           'fontSize': '14px',
                           'fontWeight': '500',
                           'display': 'inline-block',
                           'transition': 'all 0.2s',
                           'boxShadow': '0 2px 4px rgba(107, 114, 128, 0.3)'
                       })
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'})
        ], style={
            'marginBottom': '25px',
            'padding': '20px',
            'borderRadius': '12px',
            'transition': 'all 0.3s ease'
        }),
        
        # Import/Export status message
        html.Div(id='import-export-status', style={'marginBottom': '15px', 'fontSize': '13px'}),
        
        # Add ticker section
        html.Div(className='theme-card', children=[
            html.Label('➕ Add New Holding',
                      className='theme-label',
                      style={
                          'marginBottom': '12px',
                          'fontWeight': '600',
                          'fontSize': '14px',
                          'display': 'block'
                      }),
            html.Div([
                dcc.Input(
                    id='new-ticker-input',
                    type='text',
                    placeholder='Enter ticker (e.g., AAPL)',
                    style={
                        'flex': '1',
                        'padding': '12px 16px',
                        'border': '2px solid #e2e8f0',
                        'borderRadius': '8px',
                        'fontSize': '14px',
                        'outline': 'none',
                        'transition': 'all 0.2s'
                    }
                ),
                html.Button('+ Add Holding', id='add-ticker-button', n_clicks=0,
                           style={
                               'backgroundColor': '#3b82f6',
                               'color': 'white',
                               'border': 'none',
                               'padding': '12px 24px',
                               'cursor': 'pointer',
                               'borderRadius': '8px',
                               'fontSize': '14px',
                               'fontWeight': '500',
                               'marginLeft': '10px',
                               'transition': 'all 0.2s',
                               'boxShadow': '0 2px 4px rgba(59, 130, 246, 0.3)'
                           })
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'marginBottom': '25px',
            'padding': '20px',
            'borderRadius': '12px',
            'transition': 'all 0.3s ease'
        }),
        
        # Portfolio holdings table
        html.Div(id='portfolio-container', children=[]),
        
        # Total allocation display
        html.Div(id='total-allocation', style={
            'marginTop': '20px',
            'fontSize': '16px',
            'fontWeight': '600'
        }),
        
        # Save status
        html.Div(id='save-status', style={
            'marginTop': '10px',
            'fontSize': '13px',
            'color': '#10b981',
            'fontWeight': '500'
        }),
        
        # Benchmark and date inputs
        html.Div([
            html.H3('⚙️ Benchmark & Settings', 
                   style={
                       'color': '#2d3748',
                       'marginTop': '30px',
                       'marginBottom': '20px',
                       'fontSize': '20px',
                       'fontWeight': '600'
                   }),
            html.Label('Benchmark Ticker',
                      style={
                          'marginBottom': '8px',
                          'fontWeight': '600',
                          'fontSize': '13px',
                          'color': '#4a5568',
                          'display': 'block'
                      }),
            dcc.Input(
                id='benchmark-input',
                type='text',
                placeholder='e.g., SPY',
                value='SPY',
                style={
                    'marginBottom': '20px',
                    'padding': '12px 16px',
                    'width': '100%',
                    'border': '2px solid #e2e8f0',
                    'borderRadius': '8px',
                    'fontSize': '14px',
                    'boxSizing': 'border-box'
                }
            ),
            html.Label('Start Date (Optional)',
                      style={
                          'marginBottom': '8px',
                          'fontWeight': '600',
                          'fontSize': '13px',
                          'color': '#4a5568',
                          'display': 'block'
                      }),
            dcc.Input(
                id='start-date-input',
                type='text',
                placeholder='YYYY-MM-DD or leave blank for auto',
                style={
                    'marginBottom': '20px',
                    'padding': '12px 16px',
                    'width': '100%',
                    'border': '2px solid #e2e8f0',
                    'borderRadius': '8px',
                    'fontSize': '14px',
                    'boxSizing': 'border-box'
                }
            ),
            html.Button('🚀 Run Backtest', id='run-button', n_clicks=0,
                       style={
                           'backgroundColor': '#10b981',
                           'color': 'white',
                           'border': 'none',
                           'padding': '16px 32px',
                           'cursor': 'pointer',
                           'borderRadius': '10px',
                           'width': '100%',
                           'fontSize': '16px',
                           'fontWeight': '600',
                           'marginTop': '10px',
                           'transition': 'all 0.2s',
                           'boxShadow': '0 4px 6px rgba(16, 185, 129, 0.4)',
                           'textTransform': 'uppercase',
                           'letterSpacing': '0.5px'
                       })
        ])
    ], style={
        'width': '35%',
        'padding': '30px',
        'borderRadius': '16px',
        'height': 'fit-content',
        'transition': 'all 0.3s ease'
    })


def create_results_panel():
    """Create the right column results panel"""
    return html.Div([
        # Control buttons section
        html.Div(className='theme-card', children=[
            # Log Scale Toggle
            html.Button('📈 Toggle Log Scale', 
                       id='toggle-log-returns-button',
                       n_clicks=0,
                       style={
                           'backgroundColor': '#3b82f6',
                           'color': 'white',
                           'border': 'none',
                           'padding': '12px 24px',
                           'cursor': 'pointer',
                           'borderRadius': '8px',
                           'fontSize': '14px',
                           'fontWeight': '500',
                           'transition': 'all 0.2s',
                           'boxShadow': '0 2px 4px rgba(59, 130, 246, 0.3)',
                           'marginRight': '15px'
                       }),
            html.Div(id='log-returns-status', 
                    style={
                        'display': 'inline-block',
                        'verticalAlign': 'middle',
                        'fontSize': '14px',
                        'fontWeight': '500',
                        'color': '#4a5568',
                        'marginRight': '15px'
                    }),
            # Export Metrics Button
            html.Button('📊 Export Full Report', 
                       id='export-metrics-button',
                       n_clicks=0,
                       style={
                           'backgroundColor': '#f59e0b',
                           'color': 'white',
                           'border': 'none',
                           'padding': '12px 24px',
                           'cursor': 'pointer',
                           'borderRadius': '8px',
                           'fontSize': '14px',
                           'fontWeight': '500',
                           'transition': 'all 0.2s',
                           'boxShadow': '0 2px 4px rgba(245, 158, 11, 0.3)'
                       }),
            dcc.Download(id='download-metrics')
        ], style={
            'textAlign': 'center',
            'marginBottom': '30px',
            'padding': '20px',
            'borderRadius': '12px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'flexWrap': 'wrap',
            'gap': '10px',
            'transition': 'all 0.3s ease'
        }),
        
        # Results display
        dcc.Loading(
            id="loading-results",
            children=[html.Div(id='backtest-results', style={'overflowX': 'auto', 'width': '100%'})],
            type="default",
            color='#667eea'
        )
    ], style={
        'width': '60%',
        'display': 'flex',
        'flexDirection': 'column'
    })

