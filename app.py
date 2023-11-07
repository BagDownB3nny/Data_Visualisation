# Import packages
from dash import Dash, html, dash_table, dcc
import dash_leaflet as dl
import pandas as pd
import plotly.express as px
import json
from dash.dependencies import Input, Output
import geopandas as gpd

# Import functions
from data_processing import add_towns_with_no_hdb_data, filter_df_by_date, group_table, get_statistics_median_by_town
from data_retrieval import get_detailed_overview_by_month_and_town, get_map_data, get_overview_by_month_data, get_overview_data_by_month_and_town_data, get_detailed_overview_by_month_data, get_storey_range_overview_by_month, get_flat_type_overview_by_month

# Import components
from components.time_slider import time_slider
from components.boxplot import boxplot, get_overview_by_month_boxplot_figure
from components.filter import filter, storey_range_options, flat_type_options

# Load the GeoJSON file
geojson = get_map_data()

# Load the HDB resale data
overview_by_month = get_overview_by_month_data()
detailed_overview_by_month = get_detailed_overview_by_month_data()

overview_by_month_and_town = get_overview_data_by_month_and_town_data()
overview_by_month_and_town = add_towns_with_no_hdb_data(overview_by_month_and_town, geojson)

detailed_overview_by_month_and_town = get_detailed_overview_by_month_and_town()
overview_by_month_and_town = add_towns_with_no_hdb_data(detailed_overview_by_month_and_town, geojson)

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='My First App with Data'),
    dcc.Dropdown(['resale_price_median', 'price_per_sqm_median'], 'resale_price_median', id='statistic-dropdown'),
    dcc.Dropdown(options=['flat_type', 'storey_range'], value='flat_type', id='primary-filter-dropdown'),
    dcc.Dropdown(options=['All', *flat_type_options], value='All', id='secondary-filter-dropdown'),
    dcc.Graph(id='map'),
    time_slider(),
    html.Div(id='time-slider-output'),
    html.Div(id='map-click-data'),
    dcc.Graph(id='boxplot'),
])

# Callbacks
@app.callback(
    Output('secondary-filter-dropdown', 'options'),
    Output('secondary-filter-dropdown', 'value'),
    Output('map', 'figure'),
    Output('time-slider-output', 'children'),
    Output('map-click-data', 'children'),
    Output('boxplot', 'figure'),
    Input('time-slider', 'value'),
    Input('statistic-dropdown', 'value'),
    Input('primary-filter-dropdown', 'value'),
    Input('secondary-filter-dropdown', 'value'),
    [Input('map', 'clickData')],
)
def update_time_slider(time_slider_value, statistic_dropdown_value, primary_filter, secondary_filter, map_click_data):


    def get_secondary_filter_config(primary_filter, secondary_filter):

        def get_secondary_filter_options(primary_filter, secondary_filter):
            if primary_filter == 'storey_range':
                return ['All', *storey_range_options]
            elif primary_filter == 'flat_type':
                return ['All', *flat_type_options]

        def get_secondary_filter_value(secondary_filter):
            if primary_filter == 'storey_range' and secondary_filter not in storey_range_options:
                return 'All'
            elif primary_filter == 'flat_type' and secondary_filter not in flat_type_options:
                return 'All'
            else:
                return secondary_filter

        secondary_filter_options = get_secondary_filter_options(primary_filter, secondary_filter)
        secondary_filter_value = get_secondary_filter_value(secondary_filter)
        return secondary_filter_options, secondary_filter_value

    def num_to_date(num):
        year = 1990 + (num // 12)
        month = num % 12 + 1
        return f'{year}-{month}'
    start_date = num_to_date(time_slider_value[0])
    end_date = num_to_date(time_slider_value[1])
    string_output = f"Showing data from between {start_date} and {end_date}"

    def generate_map_figure():
        if secondary_filter == 'All':
            map_df = overview_by_month_and_town
        else:
            map_df = detailed_overview_by_month_and_town
            map_df = map_df[map_df[f'{primary_filter}'] == secondary_filter]

        map_df = filter_df_by_date(start_date, end_date, map_df)
        map_df = add_towns_with_no_hdb_data(map_df, geojson)
        statistics_by_town = get_statistics_median_by_town(map_df)
        
        # Create the choropleth figure and update geos
        map_figure = px.choropleth(statistics_by_town, geojson=geojson, color=statistic_dropdown_value,
                            locations='town', featureidkey='properties.PLN_AREA_N')
        map_figure.update_geos(fitbounds="locations", visible=False)
        return map_figure

    def generate_boxplot_figure():

        def generate_boxplot_figure_for_singapore(primary_filter, secondary_filter):
            if secondary_filter == 'All':
                boxplots_df = overview_by_month
            elif primary_filter == 'storey_range':
                boxplots_df = get_storey_range_overview_by_month(secondary_filter)
            elif primary_filter == 'flat_type':
                boxplots_df = get_flat_type_overview_by_month(secondary_filter)
            boxplots_df = filter_df_by_date(start_date, end_date, boxplots_df)
            boxplots_figure = get_overview_by_month_boxplot_figure(boxplots_df, statistic_dropdown_value)
            return boxplots_figure

        def generate_boxplot_figure_for_town(town, primary_filter, secondary_filter):
            town = town.replace('/', '|')
            town = town.replace(' ', '_')
            town_folder = f'./data/resale_price_data/processed_data/town_data/{town}'
            if secondary_filter == 'All':
                filename = f'{town}_overview.csv'
                fullpath = f'{town_folder}/{filename}'
            else:
                primary_filter = primary_filter.replace(' ', '_')
                primary_filter_folder = f'{town}_{primary_filter}_data'
                secondary_filter = secondary_filter.replace(' ', '_')
                filename = f'{secondary_filter}_overview.csv'
                fullpath = f'{town_folder}/{primary_filter_folder}/{filename}'

            boxplots_df = pd.read_csv(fullpath)
            boxplots_df = filter_df_by_date(start_date, end_date, boxplots_df)
            boxplots_figure = get_overview_by_month_boxplot_figure(boxplots_df, statistic_dropdown_value)
            return boxplots_figure

        if map_click_data == None:
            return generate_boxplot_figure_for_singapore(primary_filter, secondary_filter)
        else:
            town = map_click_data['points'][0]['location']
            return generate_boxplot_figure_for_town(town, primary_filter, secondary_filter)

    def generate_town_string(map_click_data):
        if map_click_data == None:
            return 'Currently viewing data of Singapore'
        else:
            return f"Currently viewing data of {map_click_data['points'][0]['location']}"

    secondary_filter_options, secondary_filter_value = get_secondary_filter_config(primary_filter, secondary_filter)
    map_figure = generate_map_figure()
    town_string_output = generate_town_string(map_click_data)
    boxplots_figure = generate_boxplot_figure()

    return secondary_filter_options, secondary_filter_value, map_figure, string_output, town_string_output, boxplots_figure

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
