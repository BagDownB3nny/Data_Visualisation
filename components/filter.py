# Import packages
from dash import Dash, html, dash_table, dcc

# declare constants
storey_range_options = ['2 ROOM', '3 ROOM', '4 ROOM', '5 ROOM', 'EXECUTIVE']
flat_type_options = ['01 TO 03', '04 TO 06', '07 TO 09', '10 TO 12', '13 AND GREATER']

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