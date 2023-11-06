from data_retrieval import get_all_raw_hdb_data

def quantile_25(x):
        return x.quantile(0.25)

def quantile_75(x):
    return x.quantile(0.75)

# create a new table with the following columns: town, month, flat_type, storey_range, 
# resale_price_median, resale_price_min, resale_price_max, 25th percentile resale_price, 75th percentile resale_price
# floor_area_sqm_median, floor_area_sqm_min, floor_area_sqm_max, 25th percentile floor_area_sqm, 75th percentile floor_area_sqm
def group_table(df):
    df = df.groupby(['town', 'month', 'flat_type', 'storey_range'])
    df = df.agg({'resale_price': ['median', 'min', 'max', quantile_25, quantile_75],
                 'floor_area_sqm': ['median', 'min', 'max', quantile_25, quantile_75]}).reset_index()
    df.columns = ['_'.join(col).rstrip('_') for col in df.columns.values]
    df.to_csv('./data/resale_price_data/ProcessedResaleFlatPrices.csv')
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
    return df

def create_overview_by_month():
    df = get_all_raw_hdb_data()

    # add new column which is resale_price / floor_area_sqm
    df['price_per_sqm'] = df['resale_price'] / df['floor_area_sqm']

    df = df.groupby(['month'])
    df = df.agg({'resale_price': ['median', 'min', 'max', quantile_25, quantile_75],
                 'price_per_sqm': ['median', 'min', 'max', quantile_25, quantile_75]}).reset_index()
    df.columns = ['_'.join(col).rstrip('_') for col in df.columns.values]
    df.to_csv('./data/resale_price_data/processed_data/overview_by_month.csv')
    return df