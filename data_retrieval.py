import pandas as pd
import geopandas as gpd

def get_hdb_data():
    df1 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonApprovalDate19901999.csv')
    df2 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonApprovalDate2000Feb2012.csv')
    df3 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv')
    df4 = pd.read_csv('./data/resale_price_data/ResaleFlatPricesBasedonRegistrationDateFromJan2015toDec2016.csv')
    df5 = pd.read_csv('./data/resale_price_data/ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv')
    df = pd.concat([df1, df2, df3, df4, df5])
    return df

def get_map_data():
    geojson = gpd.read_file("./data/map_data/SubzoneBoundaryProcessed.geojson")
    return geojson