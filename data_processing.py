import pandas as pd

def add_towns_with_no_hdb_data(df, geojson):
    # Get the list of PLN_AREA_N values in the GeoJSON file
    pln_area_n_values = [feature for feature in geojson['PLN_AREA_N']]

    # Find the PLN_AREA_N values that are in the GeoJSON file but not in the DataFrame
    missing_pln_area_n = [pln_area_n for pln_area_n in pln_area_n_values if pln_area_n not in df['town'].values]

    # Create a new DataFrame with the missing towns
    #town,month,flat_type,storey_range,resale_price_median,resale_price_min,resale_price_max,resale_price_quantile_25,resale_price_quantile_75,floor_area_sqm_median,floor_area_sqm_min,floor_area_sqm_max,floor_area_sqm_quantile_25,floor_area_sqm_quantile_75
    missing_df = pd.DataFrame({
        'town': missing_pln_area_n,
        'month': None,
        'flat_type': None,
        'storey_range': None,
        'resale_price_median': 0,
        'resale_price_min': 0,
        'resale_price_max': 0,
        'resale_price_quantile_25': 0,
        'resale_price_quantile_75': 0,
        'floor_area_sqm_median': 0,
        'floor_area_sqm_min': 0,
        'floor_area_sqm_max': 0,
        'floor_area_sqm_quantile_25': 0,
        'floor_area_sqm_quantile_75': 0
    })

    # Append the new DataFrame to the original DataFrame
    df = df._append(missing_df, ignore_index=True)
    return df

def get_months_from_date(date):
        if pd.isnull(date):
            return 0
        year = int(date[:4])
        month = int(date[5:])
        months_since_1990_jan = (year - 1990) * 12 + month
        return months_since_1990_jan

# date in the format of 2000-01
def filter_df_by_date(start_date, end_date, df):
    df = df[df['month'].apply(get_months_from_date) >= get_months_from_date(start_date)]
    df = df[df['month'].apply(get_months_from_date) <= get_months_from_date(end_date)]
    return df


# groups data by town, and aggregates resale_price_median
# input: df grouped by town, month
def get_statistics_median_by_town(df):
    df = df.groupby('town').agg({'resale_price_median': 'median', 'price_per_sqm_median': 'median'}).reset_index()
    return df

# create a new table with the following columns: town, month, flat_type, storey_range, 
# resale_price_median, resale_price_min, resale_price_max, 25th percentile resale_price, 75th percentile resale_price
# floor_area_sqm_median, floor_area_sqm_min, floor_area_sqm_max, 25th percentile floor_area_sqm, 75th percentile floor_area_sqm
def group_table(df):

    def quantile_25(x):
        return x.quantile(0.25)

    def quantile_75(x):
        return x.quantile(0.75)

    df = df.groupby(['town', 'month', 'flat_type', 'storey_range'])
    df = df.agg({'resale_price': ['median', 'min', 'max', quantile_25, quantile_75],
                 'floor_area_sqm': ['median', 'min', 'max', quantile_25, quantile_75]}).reset_index()
    df.columns = ['_'.join(col).rstrip('_') for col in df.columns.values]
    return df

# group table by town, month
# then get the average resale_price, remaining_lease
# def group_table_2(df):
#     df = df.groupby(['town', 'month']).agg({'resale_price': 'mean', 'remaining_lease': 'mean'}).reset_index()
#     return df