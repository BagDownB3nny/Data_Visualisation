from dash import Dash, html, dash_table, dcc
from datetime import date

def time_slider():
    slider = dcc.RangeSlider(1, 407, 1, value=[347, 407], id='time-slider', marks=None)
    return slider