from data_retrieval import get_all_raw_hdb_data
import pandas as pd
import os

def quantile_25(x):
        return x.quantile(0.25)

def quantile_75(x):
    return x.quantile(0.75)

# create a new table with the following columns: town, month, flat_type, storey_range, 
# resale_price_median, resale_price_min, resale_price_max, 25th percentile resale_price, 75th percentile resale_price
# price_per_sqm_median, price_per_sqm_min, price_per_sqm_max, 25th percentile price_per_sqm, 75th percentile price_per_sqm
def group_table_by_town_and_month_and_flat_type_and_storey_range(df):
    df['price_per_sqm'] = df['resale_price'] / df['floor_area_sqm']
    df = df.groupby(['town', 'month', 'flat_type', 'storey_range'])
    df = df.agg({'resale_price': ['median', 'min', 'max', quantile_25, quantile_75],
                 'price_per_sqm': ['median', 'min', 'max', quantile_25, quantile_75]}).reset_index()
    df.columns = ['_'.join(col).rstrip('_') for col in df.columns.values]
    return df

# create a new table with the following columns: town, month 
# resale_price_median, resale_price_min, resale_price_max, 25th percentile resale_price, 75th percentile resale_price
# price_per_sqm_median, price_per_sqm_min, price_per_sqm_max, 25th percentile price_per_sqm, 75th percentile price_per_sqm
def group_table_by_town_and_month(df):
    df['price_per_sqm'] = df['resale_price'] / df['floor_area_sqm']
    df = df.groupby(['town', 'month'])
    df = df.agg({'resale_price': ['median', 'min', 'max', quantile_25, quantile_75],
                 'price_per_sqm': ['median', 'min', 'max', quantile_25, quantile_75]}).reset_index()
    df.columns = ['_'.join(col).rstrip('_') for col in df.columns.values]
    return df

# create a new table with the following columns: town, month
# resale_price_median, resale_price_min, resale_price_max, 25th percentile resale_price, 75th percentile resale_price
# floor_area_sqm_median, floor_area_sqm_min, floor_area_sqm_max, 25th percentile floor_area_sqm, 75th percentile floor_area_sqm
def create_overview_table():
    df = get_all_raw_hdb_data()
    
    # add new column which is resale_price / floor_area_sqm
    df['price_per_sqm'] = df['resale_price'] / df['floor_area_sqm']

    df = df.groupby(['town', 'month'])
    df = df.agg({'resale_price': ['median', 'min', 'max', quantile_25, quantile_75],
                 'price_per_sqm': ['median', 'min', 'max', quantile_25, quantile_75]}).reset_index()
    df.columns = ['_'.join(col).rstrip('_') for col in df.columns.values]
    df.to_csv('./data/resale_price_data/processed_data/overview_by_month_and_town.csv')

def create_overview_by_month():
    df = get_all_raw_hdb_data()

    # add new column which is resale_price / floor_area_sqm
    df['price_per_sqm'] = df['resale_price'] / df['floor_area_sqm']

    df = df.groupby(['month'])
    df = df.agg({'resale_price': ['median', 'min', 'max', quantile_25, quantile_75],
                 'price_per_sqm': ['median', 'min', 'max', quantile_25, quantile_75]}).reset_index()
    df.columns = ['_'.join(col).rstrip('_') for col in df.columns.values]
    df.to_csv('./data/resale_price_data/processed_data/overview_by_month.csv')

def create_table_for_each_town():
    # Load the data
    df = get_all_raw_hdb_data()

    # Group the data by 'town'
    grouped = df.groupby('town')

    # Create a new CSV for each town
    for town, group in grouped:
        if '/' in town:
            town = town.replace('/', '|')
        town = town.replace(' ', '_')
        group.to_csv(f'./data/resale_price_data/processed_data/town_data/{town}_overview.csv', index=False)

def group_data_for_each_town_csv():
    # Create a new CSV for each town
    for filename in os.listdir('./data/resale_price_data/processed_data/town_data'):
        if filename.endswith('_overview.csv'):
            df = pd.read_csv(f'./data/resale_price_data/processed_data/town_data/{filename}')
            df = group_table_by_town_and_month(df)
            df.to_csv(f'./data/resale_price_data/processed_data/town_data/{filename}', index=False)

create_table_for_each_town()
group_data_for_each_town_csv()