import pandas as pd

def add_towns_with_no_hdb_data(df, geojson):
    # Get the list of PLN_AREA_N values in the GeoJSON file
    pln_area_n_values = [feature for feature in geojson['PLN_AREA_N']]

    # Find the PLN_AREA_N values that are in the GeoJSON file but not in the DataFrame
    missing_pln_area_n = [pln_area_n for pln_area_n in pln_area_n_values if pln_area_n not in df['town'].values]

    # Create a new DataFrame with the missing towns
    missing_df = pd.DataFrame({
        'town': missing_pln_area_n,
        'flat_type': None,
        'block': None,
        'street_name': None,
        'storey_range': None,
        'floor_area_sqm': None,
        'flat_model': None,
        'lease_commence_date': None,
        'remaining_lease': None,
        'resale_price': 0
    })

    # Append the new DataFrame to the original DataFrame
    df = df._append(missing_df, ignore_index=True)

    return df