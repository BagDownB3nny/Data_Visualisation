# Import packages
from dash import Dash, html, dash_table, dcc
import dash_leaflet as dl
import pandas as pd
import plotly.express as px
import json
from dash.dependencies import Input, Output
import geopandas as gpd

# Import functions
from data_processing import add_towns_with_no_hdb_data, filter_df_by_date, group_table, get_resale_price_median_by_town
from data_retrieval import get_hdb_data, get_map_data, get_overview_by_month_data, get_overview_data_by_month_and_town_data

# Import components
from components.time_slider import time_slider
from components.boxplot import boxplot, get_overview_by_month_boxplot_figure

# Load the GeoJSON file
geojson = get_map_data()

# Load the HDB resale data
overview_by_month = get_overview_by_month_data()

overview_by_month_and_town = get_overview_data_by_month_and_town_data()
overview_by_month_and_town = add_towns_with_no_hdb_data(overview_by_month_and_town, geojson)

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='My First App with Data'),
    dcc.Dropdown(['Resale price', 'Price per sq ft'], 'Price per sq ft'),
    dcc.Graph(id='map'),
    time_slider(),
    dash_table.DataTable(id='table', page_size=10),
    html.Div(id='time-slider-output'),
    dcc.Graph(id='boxplot'),
    #table with 10 entries per page
])

# Callbacks
@app.callback(
    Output('time-slider-output', 'children'),
    Output('map', 'figure'),
    Output('table', 'data'),
    Output('boxplot', 'figure'),
    Input('time-slider', 'value')
)
def update_time_slider(value):
    def num_to_date(num):
        year = 1990 + (num // 12)
        month = num % 12 + 1
        return f'{year}-{month}'
    start_date = num_to_date(value[0])
    end_date = num_to_date(value[1])
    string_output = f"Showing data from between {start_date} and {end_date}"


    new_overview_by_month_and_town = filter_df_by_date(num_to_date(value[0]), num_to_date(value[1]), overview_by_month_and_town)
    new_overview_by_month_and_town = add_towns_with_no_hdb_data(new_overview_by_month_and_town, geojson)

    resale_price_median_by_town = get_resale_price_median_by_town(new_overview_by_month_and_town)
    
    # Create the choropleth figure and update geos
    map_figure = px.choropleth(resale_price_median_by_town, geojson=geojson, color='resale_price_median',
                        locations='town', featureidkey='properties.PLN_AREA_N')
    map_figure.update_geos(fitbounds="locations", visible=False)


    boxplots_figure = get_overview_by_month_boxplot_figure(overview_by_month, start_date, end_date)

    return string_output, map_figure, new_overview_by_month_and_town.to_dict('records'), boxplots_figure

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
