The processed_data folder contains CSVs that have been pre-computed in order to speed up the visualisation process

overview_by_month.csv:

- Shows data for all towns each month
- Groups data by month
- Contains floor_area_sqm and resale_price statistics for each month
- Statistics include median, min, max, 25th percentile, 75th percentile
- Used for the overview boxplot (no towns selected)

overview_by_month_and_town.csv:

- Shows data for individual towns each month
- Groups data by town and month
- Contains floor_area_sqm and resale_price statistics for each group
- Statistics include median, min, max, 25th percentile, 75th percentile
- Used for the map
- Used for the overview boxplot (towns selected)

detailed_overview.csv:

- Groups resale data by town, flat_type, storey_range and month
- Contains floor_area_sqm and resale_price statistics for each group
- Statistics include median, min, max, 25th percentile, 75th percentile