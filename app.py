from dash import Dash, html, dcc, Input, Output, callback, State
import io
from data_retrieval import get_all_hdb_data, get_map_data
import pandas as pd
from itertools import islice
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import json

# Load data
geodf = get_map_data()
geojson = json.loads(geodf.to_json())
df = get_all_hdb_data()
# Get categories
flat_types = sorted(pd.unique(df['flat_type']))
storey_ranges = sorted(pd.unique(df['storey_range']))
years = sorted(df['year'].astype(str).unique())
# Dict for years and corresponding index on range slider
year_marks = dict(enumerate(years)) 
# Get colorscale for towns
towns = geodf['PLN_AREA_N']
town_colors = px.colors.sample_colorscale('hsv', [town/(towns.count()-1) for town in range(towns.count())])
town_color_map = dict(zip(towns, town_colors))

app = Dash(__name__)
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    dcc.RangeSlider(
        allowCross=False,
        id="date-slider-input",
        min=0,
        max=len(years)-1,
        marks=year_marks,
        value=[0, len(years)-1],
        step=1,
    ),
    html.Div(
        id='date-div'
    ),
    html.Div(children='Statistic'),
    dcc.Dropdown(
        id='statistic-input',
        options=[
            {'label' : 'Resale Price per sqm', 'value' : 'resale_price_per_sqm'}, 
            {'label' : 'Resale Price', 'value' : 'resale_price'}, 
            {'label' : 'Floor Area', 'value' : 'floor_area_sqm'}, 
        ],
        value='resale_price_per_sqm'
    ),
    html.Div(children=[
        html.Div(children='Flat Type'),
        dcc.Checklist(
            id='flat-type-input',
            options=flat_types,
            value=flat_types
        ),
        html.Div(children='Storey Range'),
        dcc.Checklist(
            id='storey-range-input',
            options=storey_ranges,
            value=storey_ranges
        ),
    ],
    style={'display': 'flex'}),
    dcc.Loading(
        id='map-loader',
        type='circle',
        children=[
            html.Div(
                children=[
                    html.Div(
                        id='map',
                        style={'flex':'2'},
                    ),
                    html.Div(
                        id='town-ranking',
                        style={'flex':'1'},
                    )
                ], style={'display':'flex'}
            ),
            # Workaround no loading_state property: https://github.com/plotly/dash/issues/1441
            html.Div(
                id='load-map-on-filter'
            )
        ]
    ),
    dcc.Loading(
        id='combined-graphs-loader',
        type='circle',
        children=[
            html.Div(
                id='compare-statistic-time-series'
            ),
            html.Div(
                id='combined-statistic-time-series'
            ),
            html.Div([
                html.Div(
                    id='flat-type-area'
                ),
                html.Div(
                    id='storey-range-area'
                ),], style={'display':'flex'}),
            html.Div(
                id='load-combined-graphs-on-filter'
            )
        ]
        
    ),

    dcc.Store(
        id='filtered-data'
    )
])

@callback(
    Output(component_id='date-div', component_property='children'),
    Input(component_id='date-slider-input', component_property='value')
)
def update_date_display(date_slider_input):
    year_input = [years[date_slider_input[0]], years[date_slider_input[1]]] 
    date_div = f'Showing data from between {year_input[0]} and {year_input[1]}'
    return date_div

@callback(
    [
        Output(component_id='filtered-data', component_property='data'),
        Output(component_id='load-map-on-filter', component_property='children'),
        Output(component_id='load-combined-graphs-on-filter', component_property='children')
    ],
    [
        Input(component_id='statistic-input', component_property='value'),
        Input(component_id='flat-type-input', component_property='value'),
        Input(component_id='storey-range-input', component_property='value'),
        Input(component_id='date-slider-input', component_property='value'),
    ]
)
def update_data(statistic_input, flat_type_input, storey_range_input, date_slider_input):
    year_input = [years[date_slider_input[0]], years[date_slider_input[1]]] 
    
    # Apply selected filters to dataset
    flat_types_filter = df['flat_type'].isin(flat_type_input)
    storey_ranges_filter = df['storey_range'].isin(storey_range_input)
    years_filter = pd.to_datetime(df['year'], format='%Y').between(pd.to_datetime(year_input[0], format='%Y'), pd.to_datetime(year_input[1], format='%Y'))
    filtered_df = df[flat_types_filter & storey_ranges_filter & years_filter]

    # Group filtered data by town
    filtered_df_by_town = filtered_df.groupby(by=['town'])[statistic_input].median().reset_index().sort_values(by=statistic_input)
    # Group filtered data by town and year
    filtered_df_by_town_and_year = filtered_df.groupby(by=['town', 'year'])[statistic_input].median()
    filtered_df_by_town_and_year = filtered_df_by_town_and_year.unstack().stack(dropna=False).rename(statistic_input).reset_index(level=['town', 'year']) # Fill missing years with NaN for gaps in line plot

    # Get unavailable data by town
    all_towns = geodf['PLN_AREA_N']
    available_towns = filtered_df_by_town['town'].unique()
    unavailable_towns = np.setdiff1d(all_towns, available_towns, assume_unique=True)
    unavailable_df_by_town = pd.DataFrame({'town': unavailable_towns, statistic_input: 0})

    filtered_data = {
        'filtered_df': filtered_df.to_json(orient='split', date_format='iso'),
        'filtered_df_by_town': filtered_df_by_town.to_json(orient='split', date_format='iso'),
        'filtered_df_by_town_and_year': filtered_df_by_town_and_year.to_json(orient='split', date_format='iso'),
        'unavailable_df_by_town': unavailable_df_by_town.to_json(orient='split', date_format='iso')
    }
    
    return json.dumps(filtered_data), None, None

@callback(
    [ 
        Output(component_id='map', component_property='children'),
        Output(component_id='town-ranking', component_property='children'),
    ],
    Input(component_id='filtered-data', component_property='data'),
    State(component_id='statistic-input', component_property='value'),
)
def update_map(filtered_data_json, statistic_input):
    filtered_data = json.loads(filtered_data_json)
    filtered_df_by_town = pd.read_json(io.StringIO(filtered_data['filtered_df_by_town']), orient='split')
    unavailable_df_by_town = pd.read_json(io.StringIO(filtered_data['unavailable_df_by_town']), orient='split')
    # Create choropleth map for filtered data by town
    map_figure = go.Figure()
    map_figure.add_trace(go.Choropleth(
        geojson=geojson,
        locations=filtered_df_by_town['town'],
        z=filtered_df_by_town[statistic_input],
        featureidkey='properties.PLN_AREA_N', 
        colorscale='blues',
        colorbar={'title': f'Median {statistic_input}'},
        hovertemplate='<b>%{location}</b><br>' + '%{z}' + '<extra></extra>'    
    ))

    # Add towns with no available data onto map
    map_figure.add_trace(go.Choropleth(
        geojson=geojson,
        locations=unavailable_df_by_town['town'],
        z=unavailable_df_by_town[statistic_input],
        featureidkey='properties.PLN_AREA_N',
        colorscale='greys',
        showscale=False,
        hovertemplate='<b>%{location}</b><br>' + 'No Available Data' + '<extra></extra>',
        hoverlabel={'bgcolor' : 'white'},       
    ))
    
    map_figure.update_geos(fitbounds="locations", visible=False)
    map_figure.update_layout(
        coloraxis_colorbar={'title':f'Median {statistic_input}'},
        clickmode='event+select',
        title=f'Median {statistic_input} By Town<br><sup>Left Click to select a town, Shift+Left Click to select multiple towns</sup>'
    )
    map_graph = dcc.Graph(figure=map_figure, id='map-graph')

    # Create bar chart for town rankings
    town_ranking_figure = px.bar(
        filtered_df_by_town, 
        x=statistic_input, 
        y='town',
        color=statistic_input,
        color_continuous_scale='blues',
        title=f'Median {statistic_input} By Town Ranking'
    )
    town_ranking_figure.update_layout(
        coloraxis_showscale=False, 
        yaxis_dtick=1, 
        xaxis_title=f'Median {statistic_input}'
    )
    town_ranking_graph = dcc.Graph(
        figure=town_ranking_figure,
        config={'modeBarButtonsToRemove':['lasso2d', 'select2d']}
    )

    return map_graph, town_ranking_graph

@callback(
    [
        Output(component_id='compare-statistic-time-series', component_property='children'),
        Output(component_id='combined-statistic-time-series', component_property='children'),
        Output(component_id='flat-type-area', component_property='children'),
        Output(component_id='storey-range-area', component_property='children'),
    ],
    [
        Input(component_id='filtered-data', component_property='data'),
        Input(component_id='map-graph', component_property='selectedData')
    ],
    State(component_id='statistic-input', component_property='value'),
)
def update_combined_graphs(filtered_data_json, selected_map_data, statistic_input):
    filtered_data = json.loads(filtered_data_json)
    filtered_df = pd.read_json(io.StringIO(filtered_data['filtered_df']), orient='split')
    filtered_df_by_town_and_year = pd.read_json(io.StringIO(filtered_data['filtered_df_by_town_and_year']), orient='split')

    if selected_map_data:
        town_selection = [point['location'] for point in selected_map_data['points']]
        filtered_df_by_town_and_year = filtered_df_by_town_and_year[filtered_df_by_town_and_year['town'].isin(town_selection)]
        filtered_df = filtered_df[filtered_df['town'].isin(town_selection)].reset_index(drop=True)

    # Create line plot
    compare_statistic_time_series_figure = px.line(
        filtered_df_by_town_and_year, 
        x='year', 
        y=statistic_input, 
        color='town',
        color_discrete_map=town_color_map,
        title=f'Median {statistic_input} By Town Over Time'
    )
    compare_statistic_time_series_figure.update_layout(
        xaxis_type='category',
        yaxis_title=f'Median {statistic_input}')
    compare_statistic_time_series_figure.update_traces(connectgaps=False)
    compare_statistic_time_series_graph = dcc.Graph(figure=compare_statistic_time_series_figure)

    # Create boxplot
    combined_statistic_time_series_figure = px.box(
        filtered_df, 
        x='year', 
        y=statistic_input, 
        points=False,
        color='year',
        title=f'Combined {statistic_input} Over Time'
    )
    combined_statistic_time_series_figure.update_layout(xaxis_type='category', xaxis_dtick=1, yaxis_title=f'{statistic_input}')
    combined_statistic_time_series_figure.update_traces(boxmean=True)
    combined_statistic_time_series_graph = dcc.Graph(figure=combined_statistic_time_series_figure)

    # Get counts for flat type categories over time
    flat_type_counts = filtered_df.groupby(by=['year', 'flat_type']).size().unstack(fill_value=0).stack().rename('count').reset_index(level=['year', 'flat_type'])
    flat_type_totals = filtered_df.groupby(by=['year']).size().rename('total').reset_index()
    flat_type_counts = flat_type_counts.merge(flat_type_totals, on='year')
    flat_type_counts['percentage'] = round(flat_type_counts['count'] / flat_type_counts['total'] * 100, 1)
    # Create stacked area chart
    flat_type_area_figure = px.area(flat_type_counts, x='year', y='count', color='flat_type', hover_data=['flat_type', 'year', 'count', 'total', 'percentage'])
    flat_type_area_figure.update_layout(xaxis_type='category', xaxis_dtick=1)
    flat_type_area_graph = dcc.Graph(figure=flat_type_area_figure)

    # Get counts for storey range categories over time
    storey_range_counts = filtered_df.groupby(by=['year', 'storey_range']).size().unstack(fill_value=0).stack().rename('count').reset_index(level=['year', 'storey_range'])
    storey_range_totals = filtered_df.groupby(by=['year']).size().rename('total').reset_index()
    storey_range_counts = storey_range_counts.merge(storey_range_totals, on='year')
    storey_range_counts['percentage'] = round(storey_range_counts['count'] / storey_range_counts['total'] * 100, 1)
    # Create stacked area chart
    storey_range_area_figure = px.area(storey_range_counts, x='year', y='count', color='storey_range', hover_data=['storey_range', 'year', 'count', 'total', 'percentage'])
    storey_range_area_figure.update_layout(xaxis_type='category', xaxis_dtick=1)
    storey_range_area_graph = dcc.Graph(figure=storey_range_area_figure)

    return compare_statistic_time_series_graph, combined_statistic_time_series_graph, flat_type_area_graph, storey_range_area_graph

if __name__ == '__main__':
    app.run(debug=True)
