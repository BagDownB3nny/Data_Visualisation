from dash import Dash, html, dcc, Input, Output, callback
from data_retrieval import get_all_hdb_data, get_map_data
import pandas as pd
from itertools import islice
import plotly.express as px

# Load data
geojson = get_map_data()
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
        value=[0, len(months)-1],
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
    dcc.Graph(
        id='map',
    ),
    dcc.Graph(
        id='boxplot',
    )
])

@callback(
    [
        Output(component_id='year-div', component_property='children'),   
        Output(component_id='map', component_property='figure'),
        Output(component_id='boxplot', component_property='figure')
    ],
    [
        Input(component_id='statistic-input', component_property='value'),
        Input(component_id='flat-type-input', component_property='value'),
        Input(component_id='storey-range-input', component_property='value'),
        Input(component_id='date-slider-input', component_property='value')
    ]
)
def update_output(statistic_input, flat_type_input, storey_range_input, date_slider_input):
    # Selected start and end months in the format [YYYY-MM, YYYY-MM]
    month_input = [months[date_slider_input[0]], months[date_slider_input[1]]] 
    year_div = f'{month_input[0]} - {month_input[1]}'
    
    # Apply selected filters to dataset
    flat_types_filter = df['flat_type'].isin(flat_type_input)
    storey_ranges_filter = df['storey_range'].isin(storey_range_input)
    months_filter = pd.to_datetime(df['month']).between(pd.to_datetime(month_input[0]), pd.to_datetime(month_input[1]))
    filtered_df = df[flat_types_filter & storey_ranges_filter & months_filter]

    # Create choropleth map
    filtered_df_by_town = filtered_df.groupby(by=['town'])[statistic_input].median().reset_index()
    map_figure = px.choropleth(filtered_df_by_town, geojson=geojson, color=statistic_input,
                        locations='town', featureidkey='properties.PLN_AREA_N')
    map_figure.update_geos(fitbounds="locations", visible=False)
    map_figure.update_layout(coloraxis_colorbar={'title':f'Median {statistic_input}'})

    # Create boxplot
    boxplot_figure = px.box(filtered_df, x='month', y=statistic_input, color='month')
    boxplot_figure.update_layout(xaxis_type='category')
    boxplot_figure.update_traces(boxmean=True)

    return year_div, map_figure, boxplot_figure

if __name__ == '__main__':
    app.run(debug=True)
