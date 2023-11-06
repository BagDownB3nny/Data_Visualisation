from dash import Dash, html, dash_table, dcc
import plotly.graph_objects as go

import sys
sys.path.append('../data_processing')

# import functions
from data_processing import get_months_from_date

def boxplot():
    return dcc.Graph(
        id='boxplot'
    )

import plotly.graph_objects as go

# df taken in should be from overview_by_month.csv
def get_overview_by_month_boxplot_figure(df, start_date, end_date, statistic_dropdown_value):
    fig = go.Figure()
    for index, row in df.iterrows():
        if get_months_from_date(row['month']) < get_months_from_date(start_date) or get_months_from_date(row['month']) > get_months_from_date(end_date):
            continue
        fig.add_trace(go.Box(
            x=[row['month']],
            q1=[row['resale_price_quantile_25']],
            median=[row['resale_price_median']],
            q3=[row['resale_price_quantile_75']],
            lowerfence=[row['resale_price_min']],
            upperfence=[row['resale_price_max']],
            name=row['month']
        ))
    return fig
