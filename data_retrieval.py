import pandas as pd
import geopandas as gpd
from data_processing import add_towns_with_no_hdb_data, group_table

def get_hdb_data():

    # data retrieval
    # df1 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonApprovalDate19901999.csv')
    # df2 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonApprovalDate2000Feb2012.csv')
    # df3 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv')
    # df4 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonRegistrationDateFromJan2015toDec2016.csv')
    # df5 = pd.read_csv('./data/resale_price_data/ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv')
    # df = pd.concat([df1, df2, df3, df4, df5])

    return pd.read_csv('./data/resale_price_data/ProcessedResaleFlatPrices.csv')

def get_all_raw_hdb_data():
    df1 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonApprovalDate19901999.csv')
    df2 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonApprovalDate2000Feb2012.csv')
    df3 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv')
    df4 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonRegistrationDateFromJan2015toDec2016.csv')
    df5 = pd.read_csv('./data/resale_price_data/ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv')
    df = pd.concat([df1, df2, df3, df4, df5])
    return df

def get_overview_by_month_data():
    return pd.read_csv('./data/resale_price_data/processed_data/overview_by_month.csv')

def get_overview_data_by_month_and_town_data():
    return pd.read_csv('./data/resale_price_data/processed_data/overview_by_month_and_town.csv')


def get_map_data():
    geojson = gpd.read_file("./data/map_data/SubzoneBoundaryProcessed.geojson")
    return geojson