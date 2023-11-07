# Import packages
from dash import Dash, html, dash_table, dcc

# declare constants
flat_type_options = ['2 ROOM', '3 ROOM', '4 ROOM', '5 ROOM', 'EXECUTIVE', 'MULTI GENERATION']
storey_range_options = ['very low', 'low', 'mid', 'high']

def storey_range_filter():
    return dcc.Checklist(
        storey_range_options,
        storey_range_options,
        inline=True,
        id='storey-range-filter'
    )

def flat_type_filter():
    return dcc.Checklist(
        flat_type_options,
        flat_type_options,
        inline=True,
        id='flat-type-filter'
    )

def filter():
    return html.Div([
        storey_range_filter(),
        flat_type_filter()
    ])