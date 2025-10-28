"""
Dashboard Callbacks Module
Contains all callback functions for the portfolio backtesting dashboard
"""

from dash import callback_context, html, dcc
from dash.dependencies import Input, Output, State, ALL
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import io
from contextlib import redirect_stdout
import base64
import logging

from backtesting_utils import get_company_name, safe_portfolio_backtest
from dashboard_utils import (
    load_cached_portfolios, save_portfolio_to_cache,
    format_portfolio_label, log_event,
    create_portfolio_table_html, format_total_allocation
)
from portfolio_io import (
    portfolio_to_csv, csv_to_portfolio,
    parse_upload_content, create_sample_csv,
    create_comprehensive_metrics_csv
)

logger = logging.getLogger(__name__)


def register_callbacks(app):
    """Register all callbacks with the Dash app"""
    
    # Clientside callback to handle theme styling with CSS
    app.clientside_callback(
        """
        function(isDarkJson) {
            const isDark = JSON.parse(isDarkJson);
            
            // Remove existing theme style
            let existingStyle = document.getElementById('theme-style');
            if (existingStyle) {
                existingStyle.remove();
            }
            
            // Create new style element
            const style = document.createElement('style');
            style.id = 'theme-style';
            
            if (isDark) {
                // Dark mode CSS
                style.innerHTML = `
                    .theme-card {
                        background-color: #1c1c1c !important;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.5) !important;
                        color: #e5e7eb !important;
                    }
                    .theme-label {
                        color: #9ca3af !important;
                    }
                    #portfolio-builder-panel h3 {
                        color: #e5e7eb !important;
                    }
                `;
            } else {
                // Light mode CSS
                style.innerHTML = `
                    .theme-card {
                        background-color: white !important;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.06) !important;
                        color: #1f2937 !important;
                    }
                    .theme-label {
                        color: #4a5568 !important;
                    }
                    #portfolio-builder-panel h3 {
                        color: #2d3748 !important;
                    }
                `;
            }
            
            document.head.appendChild(style);
            return window.dash_clientside.no_update;
        }
        """,
        Output('app-container', 'data-theme'),
        Input('dark-mode', 'children')
    )
    
    @app.callback(
        [Output('main-container', 'style'),
         Output('portfolio-builder-panel', 'style'),
         Output('dark-mode-toggle', 'children'),
         Output('dark-mode', 'children')],
        Input('dark-mode-toggle', 'n_clicks'),
        State('dark-mode', 'children')
    )
    def toggle_dark_mode(n_clicks, dark_mode_json):
        """Toggle between light and dark mode"""
        if n_clicks is None:
            n_clicks = 0
        
        # Get current dark mode state
        is_dark = json.loads(dark_mode_json) if dark_mode_json else False
        
        # Toggle on button click
        if n_clicks > 0:
            is_dark = not is_dark
        
        # Define theme styles
        if is_dark:
            # Dark mode styles
            main_style = {
                'padding': '0',
                'backgroundColor': '#0d1117',
                'minHeight': '100vh',
                'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                'transition': 'all 0.3s ease',
                'color': '#e5e7eb'
            }
            panel_style = {
                'width': '35%',
                'padding': '30px',
                'backgroundColor': '#1c1c1c',
                'borderRadius': '16px',
                'height': 'fit-content',
                'transition': 'all 0.3s ease',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.5)'
            }
            button_text = '☀️ Light Mode'
        else:
            # Light mode styles
            main_style = {
                'padding': '0',
                'backgroundColor': '#f0f2f5',
                'minHeight': '100vh',
                'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                'transition': 'all 0.3s ease'
            }
            panel_style = {
                'width': '35%',
                'padding': '30px',
                'backgroundColor': 'white',
                'borderRadius': '16px',
                'height': 'fit-content',
                'transition': 'all 0.3s ease',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.07)'
            }
            button_text = '🌙 Dark Mode'
        
        return main_style, panel_style, button_text, json.dumps(is_dark)
    
    
    @app.callback(
        Output('download-sample-link', 'href'),
        Input('download-sample-link', 'id')
    )
    def provide_sample_csv(_):
        """Provide sample CSV template"""
        csv_str = create_sample_csv()
        csv_encoded = base64.b64encode(csv_str.encode()).decode()
        return f"data:text/csv;base64,{csv_encoded}"
    
    
    @app.callback(
        [Output('portfolio-data', 'children', allow_duplicate=True),
         Output('company-names', 'children', allow_duplicate=True),
         Output('import-export-status', 'children')],
        Input('upload-portfolio', 'contents'),
        [State('upload-portfolio', 'filename'),
         State('portfolio-data', 'children'),
         State('company-names', 'children')],
        prevent_initial_call=True
    )
    def import_portfolio(contents, filename, current_portfolio_json, current_names_json):
        """Handle portfolio import from CSV"""
        if not contents:
            return current_portfolio_json, current_names_json, ""
        
        # Parse upload
        csv_content, parse_error = parse_upload_content(contents, filename)
        if parse_error:
            return (current_portfolio_json, current_names_json,
                    html.Div(f"❌ {parse_error}", style={'color': '#e74c3c', 'fontWeight': 'bold'}))
        
        # Convert CSV to portfolio
        portfolio, company_names, csv_error = csv_to_portfolio(csv_content)
        if csv_error:
            return (current_portfolio_json, current_names_json,
                    html.Div(f"❌ {csv_error}", style={'color': '#e74c3c', 'fontWeight': 'bold'}))
        
        # Fetch missing company names
        for ticker in portfolio.keys():
            if ticker not in company_names:
                company_names[ticker] = get_company_name(ticker)
        
        log_event('Portfolio imported', tickers=list(portfolio.keys()))
        
        return (json.dumps(portfolio), json.dumps(company_names),
                html.Div(f"✓ Imported {len(portfolio)} holdings from {filename}", 
                        style={'color': '#27ae60', 'fontWeight': 'bold'}))
    
    
    @app.callback(
        Output('download-portfolio', 'data'),
        Input('export-button', 'n_clicks'),
        [State('portfolio-data', 'children'),
         State('company-names', 'children')],
        prevent_initial_call=True
    )
    def export_portfolio(n_clicks, portfolio_json, company_names_json):
        """Handle portfolio export to CSV"""
        if not n_clicks or not portfolio_json:
            return None
        
        portfolio = json.loads(portfolio_json)
        company_names = json.loads(company_names_json) if company_names_json else {}
        
        if not portfolio:
            return None
        
        csv_str = portfolio_to_csv(portfolio, company_names)
        log_event('Portfolio exported', tickers=list(portfolio.keys()))
        
        return dict(content=csv_str, filename='portfolio_allocation.csv')
    
    
    @app.callback(
        Output('download-metrics', 'data'),
        Input('export-metrics-button', 'n_clicks'),
        [State('portfolio-data', 'children'),
         State('benchmark-input', 'value'),
         State('start-date-input', 'value')],
        prevent_initial_call=True
    )
    def export_metrics(n_clicks, portfolio_json, benchmark, start_date):
        """Export comprehensive backtest metrics and performance data to CSV"""
        if not n_clicks or not portfolio_json:
            return None
        
        try:
            portfolio = json.loads(portfolio_json)
            if not portfolio:
                return None
            
            tickers = list(portfolio.keys())
            allocations = list(portfolio.values())
            benchmark = benchmark.strip().upper() if benchmark else 'SPY'
            
            # Run backtest
            results, error_message, warning_message = safe_portfolio_backtest(
                tickers, allocations, benchmark, start_date
            )
            
            if error_message or not results:
                return None
            
            # Calculate additional metrics (same as in results display)
            calculated_metrics = calculate_additional_metrics(results)
            
            # Create comprehensive CSV with time series and metrics
            csv_str = create_comprehensive_metrics_csv(results, calculated_metrics, benchmark)
            
            log_event('Comprehensive metrics exported', 
                     data_points=len(results.prices), 
                     tickers=','.join(tickers))
            
            return dict(content=csv_str, filename='backtest_comprehensive_report.csv')
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return None
    
    
    @app.callback(
        Output('saved-portfolios-dropdown', 'options'),
        Input('interval-component', 'n_intervals')
    )
    def update_saved_portfolios_dropdown(n):
        """Update dropdown with saved portfolios"""
        portfolios = load_cached_portfolios()
        options = []
        
        for i, portfolio_data in enumerate(portfolios):
            options.append({
                'label': format_portfolio_label(portfolio_data),
                'value': i
            })
        
        return options
    
    
    @app.callback(
        [Output('backtest-results', 'children'),
         Output('log-returns-status', 'children'),
         Output('log-returns-mode', 'children')],
        [Input('run-button', 'n_clicks'),
         Input('toggle-log-returns-button', 'n_clicks')],
        [State('portfolio-data', 'children'),
         State('benchmark-input', 'value'),
         State('start-date-input', 'value'),
         State('log-returns-mode', 'children')]
    )
    def update_backtest_results(n_clicks, log_toggle_clicks, portfolio_json, 
                                benchmark, start_date, log_mode_json):
        """Run backtest and update results display"""
        log_event('update_backtest_results triggered', n_clicks=n_clicks)
        ctx = callback_context
        
        # Handle None n_clicks
        if n_clicks is None:
            n_clicks = 0
        
        # Determine trigger
        is_log_toggle = False
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            log_event('Trigger detected', trigger_id=trigger_id)
            if trigger_id == 'toggle-log-returns-button':
                is_log_toggle = True
            elif trigger_id == 'run-button':
                log_event('Run button clicked')
        
        # Initialize log scale mode
        log_scale_active = json.loads(log_mode_json) if log_mode_json else False
        
        # Toggle if requested
        if is_log_toggle:
            log_scale_active = not log_scale_active
        
        # Initial state
        if n_clicks == 0 and not is_log_toggle:
            return (html.Div("Add holdings and click 'Run Backtest' to see results.", 
                           style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': '50px'}),
                    "", json.dumps(log_scale_active))
        
        # Run backtest
        if n_clicks > 0 or is_log_toggle:
            if not portfolio_json:
                return (html.Div("Portfolio is empty. Please add holdings.", 
                               style={'color': '#e74c3c'}),
                        "", json.dumps(log_scale_active))
            
            try:
                portfolio = json.loads(portfolio_json)
                if not portfolio:
                    return (html.Div("Portfolio is empty. Please add holdings.", 
                                   style={'color': '#e74c3c'}),
                            "", json.dumps(log_scale_active))
                
                tickers = list(portfolio.keys())
                allocations = list(portfolio.values())
                benchmark = benchmark.strip().upper() if benchmark else 'SPY'
                
                results, error_message, warning_message = safe_portfolio_backtest(
                    tickers, allocations, benchmark, start_date
                )
                
                if error_message:
                    return (html.Div(error_message, style={'color': '#e74c3c', 'marginTop': '20px'}),
                            "", json.dumps(log_scale_active))
                
                # Build results display
                results_html = build_results_display(
                    results, benchmark, log_scale_active, warning_message
                )
                
                log_status = "Log Scale: ON" if log_scale_active else "Log Scale: OFF"
                
                return (results_html, log_status, json.dumps(log_scale_active))
                
            except Exception as e:
                logger.error(f"Error in backtest: {e}")
                return (html.Div(f"Error processing results: {str(e)}", 
                               style={'color': '#e74c3c'}),
                        "", json.dumps(False))
    
    
    @app.callback(
        [Output('portfolio-container', 'children'),
         Output('portfolio-data', 'children'),
         Output('total-allocation', 'children'),
         Output('new-ticker-input', 'value'),
         Output('company-names', 'children'),
         Output('save-status', 'children')],
        [Input('add-ticker-button', 'n_clicks'),
         Input({'type': 'remove-button', 'index': ALL}, 'n_clicks'),
         Input({'type': 'weight-input', 'index': ALL}, 'value'),
         Input('saved-portfolios-dropdown', 'value')],
        [State('new-ticker-input', 'value'),
         State('portfolio-data', 'children'),
         State('company-names', 'children')]
    )
    def update_portfolio(add_clicks, remove_clicks, weight_values, 
                        selected_portfolio_idx, new_ticker, 
                        portfolio_json, company_names_json):
        """Update portfolio holdings"""
        ctx = callback_context
        log_event('Portfolio update triggered')
        
        # Initialize portfolio and names
        portfolio = json.loads(portfolio_json) if portfolio_json else {}
        company_names = json.loads(company_names_json) if company_names_json else {}
        save_status = ""
        
        # Handle loading saved portfolio
        if ctx.triggered and 'saved-portfolios-dropdown' in ctx.triggered[0]['prop_id']:
            if selected_portfolio_idx is not None:
                portfolios = load_cached_portfolios()
                if 0 <= selected_portfolio_idx < len(portfolios):
                    saved_data = portfolios[selected_portfolio_idx]
                    portfolio = saved_data['portfolio']
                    company_names = saved_data['company_names']
                    save_status = f"Loaded portfolio from {saved_data['saved_at'][:16]}"
        
        # Handle adding new ticker
        elif ctx.triggered and ctx.triggered[0]['prop_id'] == 'add-ticker-button.n_clicks':
            if new_ticker and new_ticker.strip():
                ticker = new_ticker.strip().upper()
                if ticker not in portfolio:
                    total_weight = sum(portfolio.values())
                    remaining = max(0, 1.0 - total_weight)
                    portfolio[ticker] = remaining if portfolio else 1.0
                    company_names[ticker] = get_company_name(ticker)
        
        # Handle removing ticker
        elif ctx.triggered:
            for trigger in ctx.triggered:
                if 'remove-button' in trigger['prop_id']:
                    json_str = trigger['prop_id'].rsplit('.n_clicks', 1)[0]
                    try:
                        parsed_id = json.loads(json_str)
                        ticker_to_remove = parsed_id['index']
                        if ticker_to_remove:
                            portfolio.pop(ticker_to_remove, None)
                            company_names.pop(ticker_to_remove, None)
                    except json.JSONDecodeError:
                        pass
                
                if 'weight-input' in trigger['prop_id'] and weight_values:
                    tickers = list(portfolio.keys())
                    for i, weight in enumerate(weight_values):
                        if i < len(tickers) and weight is not None:
                            try:
                                weight_decimal = max(0, min(1, float(weight) / 100.0))
                                portfolio[tickers[i]] = weight_decimal
                            except (ValueError, TypeError):
                                pass
        
        # Save to cache if modified
        if portfolio and ctx.triggered and 'saved-portfolios-dropdown' not in str(ctx.triggered):
            save_portfolio_to_cache(portfolio, company_names)
            if not save_status:
                save_status = "✓ Portfolio saved"
        
        # Build display
        table = create_portfolio_table_html(portfolio, company_names)
        total_display = format_total_allocation(portfolio) if portfolio else html.Div()
        
        return (table, json.dumps(portfolio), total_display, '', 
                json.dumps(company_names), save_status)


def build_results_display(results, benchmark, log_scale_active, warning_message):
    """Build the results display HTML"""
    stats = results.stats
    
    def safe_get(df, index, column, default='N/A', multiplier=1, format_pct=False):
        try:
            value = df.loc[index, column] * multiplier
            if format_pct and isinstance(value, (int, float)):
                return f'{value:.2f}%'
            elif isinstance(value, (int, float)):
                return f'{value:.2f}'
            return str(value)
        except:
            return default
    
    # Create performance chart
    performance_chart = create_performance_chart(results, benchmark, log_scale_active)
    
    # Create quarterly returns chart
    quarterly_chart = create_quarterly_chart(results)
    
    # Calculate additional metrics
    metrics = calculate_additional_metrics(results)
    
    # Build warning display
    warning_display = None
    if warning_message:
        warning_display = html.Div([
            html.Span('⚠️ ', style={'marginRight': '8px'}),
            html.Span(warning_message)
        ], style={
            'color': '#92400e',
            'backgroundColor': '#fef3c7',
            'padding': '12px 20px',
            'borderRadius': '10px',
            'marginBottom': '25px',
            'fontWeight': '500',
            'fontSize': '14px',
            'border': '2px solid #f59e0b',
            'boxShadow': '0 2px 4px rgba(245, 158, 11, 0.2)'
        })
    
    return html.Div([
        html.H3('🎯 Backtest Results', 
               style={
                   'color': '#1f2937',
                   'marginBottom': '25px',
                   'fontSize': '28px',
                   'fontWeight': '600'
               }),
        warning_display,
        
        # Performance metrics table
        create_metrics_table(stats, metrics, benchmark, safe_get),
        
        # Charts
        html.Div([
            dcc.Graph(id='performance-chart', figure=performance_chart)
        ], className='theme-card', style={
            'padding': '20px',
            'borderRadius': '12px',
            'marginBottom': '25px',
            'transition': 'all 0.3s ease'
        }),
        
        html.Div([
            dcc.Graph(figure=quarterly_chart)
        ], className='theme-card', style={
            'padding': '20px',
            'borderRadius': '12px',
            'marginBottom': '25px',
            'transition': 'all 0.3s ease'
        }),
        
        # Full stats
        html.Details([
            html.Summary('📊 View Full Statistics', 
                        style={
                            'cursor': 'pointer',
                            'padding': '15px 20px',
                            'backgroundColor': '#f3f4f6',
                            'borderRadius': '10px',
                            'fontWeight': '600',
                            'fontSize': '15px',
                            'color': '#374151',
                            'userSelect': 'none'
                        }),
            html.Pre(capture_display(results), 
                    style={
                        'backgroundColor': '#1f2937',
                        'color': '#f3f4f6',
                        'padding': '20px',
                        'borderRadius': '10px',
                        'whiteSpace': 'pre-wrap',
                        'wordBreak': 'break-all',
                        'marginTop': '10px',
                        'fontSize': '12px',
                        'lineHeight': '1.6',
                        'fontFamily': 'monospace'
                    })
        ], className='theme-card', style={
            'marginTop': '25px',
            'padding': '20px',
            'borderRadius': '12px',
            'transition': 'all 0.3s ease'
        })
    ], style={'padding': '20px 0'})


def create_performance_chart(results, benchmark, log_scale_active):
    """Create the performance chart"""
    try:
        portfolio_prices = results.prices['Portfolio']
        benchmark_prices = results.prices['Benchmark']
        
        # Normalize to base 100
        portfolio_data = (portfolio_prices / portfolio_prices.iloc[0]) * 100
        benchmark_data = (benchmark_prices / benchmark_prices.iloc[0]) * 100
        
        # Determine y-axis type
        yaxis_type = 'log' if log_scale_active else 'linear'
        yaxis_title = 'Value (Base = 100, Log Scale)' if log_scale_active else 'Value (Base = 100)'
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=portfolio_data.index, y=portfolio_data,
            mode='lines', name='Portfolio',
            line=dict(color='#3498db', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=benchmark_data.index, y=benchmark_data,
            mode='lines', name=f'Benchmark ({benchmark})',
            line=dict(color='#95a5a6', width=2)
        ))
        
        fig.update_layout(
            title='Portfolio Performance',
            xaxis_title='Date',
            yaxis_title=yaxis_title,
            yaxis_type=yaxis_type,
            hovermode='x unified',
            template='plotly_white',
            height=400,
            uirevision=True
        )
        
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Chart error: {str(e)}", showarrow=False)
        return fig


def create_quarterly_chart(results):
    """Create quarterly returns chart"""
    try:
        portfolio_prices = results.prices['Portfolio']
        quarterly_returns = portfolio_prices.resample('QE').last().pct_change().dropna() * 100
        
        colors = ['#27ae60' if r > 0 else '#e74c3c' for r in quarterly_returns]
        
        fig = go.Figure(data=[
            go.Bar(x=quarterly_returns.index, y=quarterly_returns,
                  marker_color=colors, name='Quarterly Returns')
        ])
        
        fig.update_layout(
            title='Quarterly Returns (%)',
            xaxis_title='Quarter',
            yaxis_title='Return (%)',
            template='plotly_white',
            height=300,
            showlegend=False
        )
        
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Chart error: {str(e)}", showarrow=False)
        return fig


def calculate_additional_metrics(results):
    """Calculate additional performance metrics"""
    try:
        portfolio_returns = results.prices['Portfolio'].pct_change().dropna()
        benchmark_returns = results.prices['Benchmark'].pct_change().dropna()
        
        trading_days = 252
        portfolio_ann_return = (1 + portfolio_returns.mean()) ** trading_days - 1
        benchmark_ann_return = (1 + benchmark_returns.mean()) ** trading_days - 1
        relative_ann_return = portfolio_ann_return - benchmark_ann_return
        
        portfolio_std = portfolio_returns.std() * np.sqrt(trading_days)
        benchmark_std = benchmark_returns.std() * np.sqrt(trading_days)
        
        correlation = results.prices['Portfolio'].corr(results.prices['Benchmark'])
        
        # Best/worst years
        yearly_returns = results.prices['Portfolio'].resample('YE').last().pct_change().dropna()
        best_year = yearly_returns.max() * 100 if not yearly_returns.empty else 'N/A'
        worst_year = yearly_returns.min() * 100 if not yearly_returns.empty else 'N/A'
        
        benchmark_yearly = results.prices['Benchmark'].resample('YE').last().pct_change().dropna()
        benchmark_best = benchmark_yearly.max() * 100 if not benchmark_yearly.empty else 'N/A'
        benchmark_worst = benchmark_yearly.min() * 100 if not benchmark_yearly.empty else 'N/A'
        
        return {
            'portfolio_ann_return': portfolio_ann_return,
            'benchmark_ann_return': benchmark_ann_return,
            'relative_ann_return': relative_ann_return,
            'portfolio_std': portfolio_std,
            'benchmark_std': benchmark_std,
            'correlation': correlation,
            'best_year': best_year,
            'worst_year': worst_year,
            'benchmark_best': benchmark_best,
            'benchmark_worst': benchmark_worst
        }
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {
            'portfolio_ann_return': 0, 'benchmark_ann_return': 0,
            'relative_ann_return': 0, 'portfolio_std': 0, 'benchmark_std': 0,
            'correlation': 'N/A', 'best_year': 'N/A', 'worst_year': 'N/A',
            'benchmark_best': 'N/A', 'benchmark_worst': 'N/A'
        }


def create_metrics_table(stats, metrics, benchmark, safe_get):
    """Create the performance metrics table"""
    
    def format_value(val):
        if isinstance(val, (int, float)):
            return f'{val:.2f}%'
        return str(val)
    
    return html.Div([
        html.Div([
            html.H4('📈 Performance Metrics', 
                   style={
                       'color': '#1f2937',
                       'marginBottom': '20px',
                       'fontSize': '22px',
                       'fontWeight': '600'
                   }),
            html.Table([
                html.Tr([
                    html.Td('Metric', style={
                        'fontWeight': '700',
                        'padding': '14px 16px',
                        'background': '#023047',
                        'color': 'white',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px'
                    }),
                    html.Td('Portfolio', style={
                        'fontWeight': '700',
                        'padding': '14px 16px',
                        'background': '#023047',
                        'color': 'white',
                        'textAlign': 'right',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px'
                    }),
                    html.Td(f'Benchmark ({benchmark})', style={
                        'fontWeight': '700',
                        'padding': '14px 16px',
                        'background': '#023047',
                        'color': 'white',
                        'textAlign': 'right',
                        'fontSize': '12px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px'
                    })
                ]),
                html.Tr([
                    html.Td('Annualized Return:', style={'padding': '14px 16px', 'backgroundColor': '#f9fafb', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(f'{metrics["portfolio_ann_return"]*100:.2f}%', 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': '#f9fafb', 'color': '#111827', 'fontSize': '14px'}),
                    html.Td(f'{metrics["benchmark_ann_return"]*100:.2f}%', 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontSize': '13px', 
                                 'color': '#6b7280', 'backgroundColor': '#f9fafb'})
                ]),
                html.Tr([
                    html.Td('Relative Return (vs Benchmark):', style={'padding': '14px 16px', 'backgroundColor': 'white', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(f'{metrics["relative_ann_return"]*100:+.2f}%', 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': 'white',
                                 'color': '#10b981' if metrics["relative_ann_return"] > 0 else '#ef4444', 'fontSize': '14px'}),
                    html.Td('—', style={'padding': '14px 16px', 'textAlign': 'right', 
                           'fontSize': '13px', 'color': '#6b7280', 'backgroundColor': 'white'})
                ]),
                html.Tr([
                    html.Td('Volatility (Std Dev):', style={'padding': '14px 16px', 'backgroundColor': '#f9fafb', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(f'{metrics["portfolio_std"]*100:.2f}%', 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': '#f9fafb', 'color': '#111827', 'fontSize': '14px'}),
                    html.Td(f'{metrics["benchmark_std"]*100:.2f}%', 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontSize': '13px', 
                                 'color': '#6b7280', 'backgroundColor': '#f9fafb'})
                ]),
                html.Tr([
                    html.Td('Sharpe Ratio:', style={'padding': '14px 16px', 'backgroundColor': 'white', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(safe_get(stats, 'daily_sharpe', 'Portfolio'), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': 'white', 'color': '#111827', 'fontSize': '14px'}),
                    html.Td(safe_get(stats, 'daily_sharpe', 'Benchmark'), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontSize': '13px', 
                                 'color': '#6b7280', 'backgroundColor': 'white'})
                ]),
                html.Tr([
                    html.Td('Sortino Ratio:', style={'padding': '14px 16px', 'backgroundColor': '#f9fafb', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(safe_get(stats, 'daily_sortino', 'Portfolio'), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': '#f9fafb', 'color': '#111827', 'fontSize': '14px'}),
                    html.Td(safe_get(stats, 'daily_sortino', 'Benchmark'), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontSize': '13px', 
                                 'color': '#6b7280', 'backgroundColor': '#f9fafb'})
                ]),
                html.Tr([
                    html.Td('CAGR:', style={'padding': '14px 16px', 'backgroundColor': 'white', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(safe_get(stats, 'cagr', 'Portfolio', multiplier=100, format_pct=True), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': 'white', 'color': '#111827', 'fontSize': '14px'}),
                    html.Td(safe_get(stats, 'cagr', 'Benchmark', multiplier=100, format_pct=True), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontSize': '13px', 
                                 'color': '#6b7280', 'backgroundColor': 'white'})
                ]),
                html.Tr([
                    html.Td('Max Drawdown:', style={'padding': '14px 16px', 'backgroundColor': '#f9fafb', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(safe_get(stats, 'max_drawdown', 'Portfolio', multiplier=100, format_pct=True), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': '#f9fafb', 'color': '#111827', 'fontSize': '14px'}),
                    html.Td(safe_get(stats, 'max_drawdown', 'Benchmark', multiplier=100, format_pct=True), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontSize': '13px', 
                                 'color': '#6b7280', 'backgroundColor': '#f9fafb'})
                ]),
                html.Tr([
                    html.Td('Correlation with Benchmark:', style={'padding': '14px 16px', 'backgroundColor': 'white', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(f'{metrics["correlation"]:.2f}' if isinstance(metrics["correlation"], (int, float)) else metrics["correlation"], 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': 'white', 'color': '#111827', 'fontSize': '14px'}),
                    html.Td('1.00', style={'padding': '14px 16px', 'textAlign': 'right', 
                           'fontSize': '13px', 'color': '#6b7280', 'backgroundColor': 'white'})
                ]),
                html.Tr([
                    html.Td('Best Year:', style={'padding': '14px 16px', 'backgroundColor': '#f9fafb', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(format_value(metrics["best_year"]), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': '#f9fafb',
                                 'color': '#10b981', 'fontSize': '14px'}),
                    html.Td(format_value(metrics["benchmark_best"]), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontSize': '13px', 
                                 'color': '#6b7280', 'backgroundColor': '#f9fafb'})
                ]),
                html.Tr([
                    html.Td('Worst Year:', style={'padding': '14px 16px', 'backgroundColor': 'white', 'color': '#374151', 'fontSize': '14px'}),
                    html.Td(format_value(metrics["worst_year"]), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontWeight': '700', 'backgroundColor': 'white',
                                 'color': '#ef4444', 'fontSize': '14px'}),
                    html.Td(format_value(metrics["benchmark_worst"]), 
                           style={'padding': '14px 16px', 'textAlign': 'right', 'fontSize': '13px', 
                                 'color': '#6b7280', 'backgroundColor': 'white'})
                ])
            ], style={
                'width': '100%',
                'tableLayout': 'fixed',
                'borderCollapse': 'separate',
                'borderSpacing': '0'
            })
        ], style={
            'padding': '25px',
            'borderRadius': '12px',
            'marginBottom': '30px',
            'maxWidth': '100%',
            'overflowX': 'auto',
            'transition': 'all 0.3s ease'
        }, className='theme-card'),
    ])


def capture_display(results):
    """Capture results.display() output as string"""
    f = io.StringIO()
    with redirect_stdout(f):
        results.display()
    return f.getvalue()

