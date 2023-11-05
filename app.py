# Import packages
from dash import Dash, html, dash_table, dcc
import dash_leaflet as dl
import pandas as pd
import plotly.express as px
import json
from dash.dependencies import Input, Output
import geopandas as gpd

# Import functions
from data_processing import add_towns_with_no_hdb_data
from data_retrieval import get_hdb_data, get_map_data

# Import components
from components.time_slider import time_slider

# Load the HDB resale data
# df = get_hdb_data()
df = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv')

# Load the GeoJSON file
# geojson = get_map_data()

# Add the missing towns to the DataFrame
# df = add_towns_with_no_hdb_data(df, geojson)

# Initialize the app
app = Dash(__name__)

# Create the choropleth figure and update geos
# fig = px.choropleth(df, geojson=geojson, color='resale_price',
#                     locations='town', featureidkey='properties.PLN_AREA_N')

# fig.update_geos(fitbounds="locations", visible=False)

# App layout
app.layout = html.Div([
    html.Div(children='My First App with Data'),
    # dcc.Graph(figure=fig),
    time_slider(),
    html.Div(id='time-slider-output', ),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    # dcc.Graph(figure= px.histogram(df, x='month', y='resale_price', histfunc='avg')),
])


months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
@app.callback(
    Output('time-slider-output', 'children'),
    Input('time-slider', 'value')
)
def update_time_slider(value):
    def num_to_date(num):
        year = 1990 + (num // 12)
        month = months[num % 12]
        return f'{month} {year}'
    return f"Showing data from between {num_to_date(value[0])} and {num_to_date(value[1])}"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
