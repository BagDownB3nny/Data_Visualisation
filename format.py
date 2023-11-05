import geopandas as gpd

# Read the GeoJSON file
gdf = gpd.read_file("./data/map_data/MasterPlan2019SubzoneBoundaryNoSeaGEOJSON.geojson")


# Sets the description column to be PLN_AREA_N
def get_town_name(description):
    start_index = description.find('<th>PLN_AREA_N</th>')
    end_index = description.find('<td>', start_index)
    content_start = end_index + 4
    content_end = description.find('</td>', content_start)
    content = description[content_start:content_end]
    return content

# Modify an existing column
gdf['Description'] = gdf['Description'].apply(get_town_name)

# # Ensure the 'geometry' column is a GeoSeries
# gdf['geometry'] = gdf['geometry'].apply(lambda x: gpd.GeoSeries(x))

# # Group by the description and merge the geometries
# gdf = gdf.groupby('Description').agg({'geometry': lambda x: x.unary_union}).reset_index()


# # Group by the description and merge the geometries
# gdf['geometry'] = gdf.groupby('Description')['geometry'].apply(lambda x: x.unary_union)

# # Group by the description
# groups = gdf.groupby('Description')

# Iterate over the groups
# for name, group in groups:
#     try:
#         # Apply the unary_union function
#         union = group['geometry'].unary_union
#         # print(f"Group {name}: {union}")
#     except Exception as e:
#         print(f"Error processing group {name}: {e}")



# Write the modified data to a new GeoJSON file
gdf.to_file("./data/map_data/SubzoneBoundaryProcessed.geojson", driver='GeoJSON')
