from dash import Dash, html, dash_table, dcc
from datetime import date

# can't get the tooltip to display the date, so I decided to switch to date_picker_range
def time_slider():

    def get_marks():
        marks = {}
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for i in range(1, 408):
            year = 1990 + (i // 12)
            month = months[i % 12]
            marks[i] = {'label': f'{month} {year}'}
        return marks

    slider = dcc.RangeSlider(1, 407, 1, value=[1, 407], id='time-slider', marks=None)
    return slider