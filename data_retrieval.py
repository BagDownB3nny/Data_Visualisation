import pandas as pd
import geopandas as gpd

def get_map_data():
    return gpd.read_file("./data/map_data/SubzoneBoundaryProcessed.geojson")

def get_all_hdb_data():
    return pd.read_csv('./data/resale_price_data/ResaleFlatPrices1990to2023Processed.csv')