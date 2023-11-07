from data_retrieval import get_all_raw_hdb_data
import pandas as pd
import os

def quantile_25(x):
        return x.quantile(0.25)

def quantile_75(x):
    return x.quantile(0.75)

# changes storey_range to 4 categories: very low, low, mid, high
# very low: 1-3
# low: 4-6
# mid: 7-9
# high: 10 onwards
def change_storey_range_to_4_categories(df):

    def change_storey_range(storey_range):
        if storey_range in ['01 TO 03']:
            return 'very low'
        elif storey_range in ['04 TO 06']:
            return 'low'
        elif storey_range in ['07 TO 09']:
            return 'mid'
        else:
            return 'high'
    df['storey_range'] = df['storey_range'].apply(change_storey_range)
    return df

# create a new table by grouping by input columns
# aggregates columns to get the following columns:
# resale_price_median, resale_price_min, resale_price_max, 25th percentile resale_price, 75th percentile resale_price
# floor_area_sqm_median, floor_area_sqm_min, floor_area_sqm_max, 25th percentile floor_area_sqm, 75th percentile floor_area_sqm
def create_new_overview(groupby_columns):
    df = get_all_raw_hdb_data()
    df = change_storey_range_to_4_categories(df)
    
    # add new column which is resale_price / floor_area_sqm
    df['price_per_sqm'] = df['resale_price'] / df['floor_area_sqm']

    df = df.groupby(groupby_columns)
    df = df.agg({'resale_price': ['median', 'min', 'max', quantile_25, quantile_75],
                 'price_per_sqm': ['median', 'min', 'max', quantile_25, quantile_75]}).reset_index()
    df.columns = ['_'.join(col).rstrip('_') for col in df.columns.values]
    return df

def create_overview_by_month_and_town():
    df = create_new_overview(['town', 'month'])
    df.to_csv(f'./data/resale_price_data/processed_data/overview_by_month_and_town.csv')

def create_overview_by_month():
    df = create_new_overview(['month'])
    df.to_csv(f'./data/resale_price_data/processed_data/overview_by_month.csv')

def create_detailed_overview_by_month():
    df = create_new_overview(['month', 'storey_range', 'flat_type'])
    df.to_csv(f'./data/resale_price_data/processed_data/detailed_overview_by_month.csv')

def create_detailed_overview_by_month_and_town():
    df = create_new_overview(['town', 'month', 'storey_range', 'flat_type'])
    df.to_csv(f'./data/resale_price_data/processed_data/detailed_overview_by_month_and_town.csv')

def create_overview_for_each_town():

    df = create_new_overview(['town', 'month'])

    # Group the data by 'town'
    grouped = df.groupby('town')

    # Create a new CSV for each town
    for town, group in grouped:
        town = town.replace('/', '|')
        town = town.replace(' ', '_')
        group.to_csv(f'./data/resale_price_data/processed_data/town_data/{town}_overview.csv', index=False)

def create_detailed_overview_for_each_town():

    df = create_new_overview(['town', 'month', 'storey_range', 'flat_type'])

    # Group the data by 'town'
    grouped = df.groupby('town')

    # Create a new CSV for each town
    for town, group in grouped:
        town = town.replace('/', '|')
        town = town.replace(' ', '_')
        group.to_csv(f'./data/resale_price_data/processed_data/town_data/{town}_detailed_overview.csv', index=False)

def create_overviews_for_each_storey_range_by_month():
    df = create_new_overview(['month', 'storey_range'])

    grouped = df.groupby('storey_range')

    for storey_range, group in grouped:
        storey_range = storey_range.replace(' ', '_')
        group.to_csv(f'./data/resale_price_data/processed_data/storey_range_data/{storey_range}_overview.csv', index=False)

def create_overviews_for_each_flat_type_by_month():
    df = create_new_overview(['month', 'flat_type'])
    df['flat_type'] = df['flat_type'].apply(lambda x: x.replace('-', ' '))
    grouped = df.groupby('flat_type')

    for flat_type, group in grouped:
        flat_type = flat_type.replace(' ', '_')
        group.to_csv(f'./data/resale_price_data/processed_data/flat_type_data/{flat_type}_overview.csv', index=False)

create_overviews_for_each_flat_type_by_month()
create_overviews_for_each_storey_range_by_month()