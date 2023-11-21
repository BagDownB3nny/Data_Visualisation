from dash import Dash, html, dcc, Input, Output, callback, ctx, State
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
months = sorted(df['month'].unique())
# Dict for years and corresponding index on range slider
date_slider_marks = dict(islice(enumerate(pd.to_datetime(df['month'].unique()).year.astype('str')), None, None, 12)) 

app = Dash(__name__)

app.layout = html.Div([
    dcc.RangeSlider(
        allowCross=False,
        id="date-slider-input",
        min=0,
        max=len(months)-1,
        marks=date_slider_marks,
        # value=[0, len(months)-1],
        value=[0, 50],
        step=1,
    ),
        html.Div(
        id='year-div'
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
    html.Div(
        id='output-div',
    ),
    html.Div(
        children=[
            dcc.Graph(
                id='map',
                style={'flex':'2'},
            ),
            dcc.Graph(
                id='bar',
                style={'flex':'1'},
                config={'modeBarButtonsToRemove':['lasso2d', 'select2d']}
            )
        ], style={'display':'flex'}
    ),

    dcc.Graph(
        id='boxplot',
    ),

    dcc.Store(
        id='filtered_data'
    )
])

@callback(
    [
        Output(component_id='year-div', component_property='children'),
        Output(component_id='filtered_data', component_property='data')
    ],
    [
        Input(component_id='statistic-input', component_property='value'),
        Input(component_id='flat-type-input', component_property='value'),
        Input(component_id='storey-range-input', component_property='value'),
        Input(component_id='date-slider-input', component_property='value'),
    ]
)
def update_data(statistic_input, flat_type_input, storey_range_input, date_slider_input):
    # Selected start and end months in the format [YYYY-MM, YYYY-MM]
    month_input = [months[date_slider_input[0]], months[date_slider_input[1]]] 
    year_div = f'{month_input[0]} - {month_input[1]}'
    
    # Apply selected filters to dataset
    flat_types_filter = df['flat_type'].isin(flat_type_input)
    storey_ranges_filter = df['storey_range'].isin(storey_range_input)
    months_filter = pd.to_datetime(df['month']).between(pd.to_datetime(month_input[0]), pd.to_datetime(month_input[1]))
    filtered_df = df[flat_types_filter & storey_ranges_filter & months_filter]

    # Group filtered data by town
    filtered_df_by_town = filtered_df.groupby(by=['town'])[statistic_input].median().reset_index().sort_values(by=statistic_input)

    # Get unavailable data by town
    all_towns = geodf['PLN_AREA_N']
    available_towns = filtered_df_by_town['town'].unique()
    unavailable_towns = np.setdiff1d(all_towns, available_towns, assume_unique=True)
    unavailable_df_by_town = pd.DataFrame({'town': unavailable_towns, statistic_input: 0})

    filtered_data = {
        'filtered_df': filtered_df.to_json(orient='split', date_format='iso'),
        'filtered_df_by_town': filtered_df_by_town.to_json(orient='split', date_format='iso'),
        'unavailable_df_by_town': unavailable_df_by_town.to_json(orient='split', date_format='iso')
    }
    
    return year_div, json.dumps(filtered_data)

@callback(
    [ 
        Output(component_id='map', component_property='figure'),
        Output(component_id='bar', component_property='figure'),
    ],
    Input(component_id='filtered_data', component_property='data'),
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
        clickmode='event+select'
    )

    # Create bar chart for town rankings
    bar_figure = px.bar(
        filtered_df_by_town, 
        x=statistic_input, 
        y='town',
        color=statistic_input,
        color_continuous_scale='blues'
    )
    bar_figure.update_layout(coloraxis_showscale=False, yaxis_dtick=1)

    return map_figure, bar_figure

@callback(
    Output(component_id='boxplot', component_property='figure'),
    Input(component_id='filtered_data', component_property='data'),
    State(component_id='statistic-input', component_property='value'),
)
def update_boxplot(filtered_data_json, statistic_input):
    filtered_data = json.loads(filtered_data_json)
    filtered_df = pd.read_json(io.StringIO(filtered_data['filtered_df']), orient='split')

    # Create boxplot
    boxplot_figure = px.box(filtered_df, x='month', y=statistic_input, color='month')
    boxplot_figure.update_layout(xaxis_type='category')
    boxplot_figure.update_traces(boxmean=True)

    return boxplot_figure


if __name__ == '__main__':
    app.run(debug=True)
