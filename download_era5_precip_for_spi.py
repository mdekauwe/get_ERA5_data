#!/usr/bin/env python3

"""
Download ERA5 monthly total precipitation (GRIB) for a small region around
Alice Holt (51.1536 N, -0.8582 W)
"""

import os
import cdsapi
import xarray as xr
import csv

def download_era5_precip(start_year, end_year, north, south, west, east,
                         output_dir):
    c = cdsapi.Client()

    for year in range(start_year, end_year + 1):
        grib_file = os.path.join(output_dir, f"era5_precip_{year}.grib")
        if os.path.exists(grib_file):
            print(f"{grib_file} already exists, skipping...")
            continue

        print(f"downloading era5 total precipitation for {year} ")
        c.retrieve(
            'reanalysis-era5-single-levels-monthly-means',
            {
                'product_type': 'monthly_averaged_reanalysis',
                'variable': 'total_precipitation',
                'year': str(year),
                'month': [f'{i:02d}' for i in range(1, 13)],
                'time': '00:00',
                'area': [north, west, south, east],
                'format': 'grib'
            },
            grib_file
        )
        print(f"downloaded {grib_file}")


def extract_pixel_to_csv(start_year, end_year, lat_point, lon_point,
                         output_dir):
    all_data = []

    for year in range(start_year, end_year + 1):
        grib_file = os.path.join(output_dir, f"era5_precip_{year}.grib")
        ds = xr.open_dataset(grib_file, engine='cfgrib', decode_times=True)

        pixel = ds.sel(latitude=lat_point, longitude=lon_point,
                       method='nearest')

        for i, time in enumerate(pixel.time.values):
            # original units m
            rain_mm = float(pixel['tp'].isel(time=i)) * 1000
            all_data.append({'time': str(time), 'rain_mm': rain_mm})

    csv_file = os.path.join(output_dir,
                            f"era5_precip_{lat_point}_{lon_point}.csv")

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['time', 'rain_mm'])
        writer.writeheader()
        writer.writerows(all_data)

if __name__ == "__main__":

    output_dir = "/Users/xj21307/Desktop/ERA5_precip"
    start_year = 1981
    end_year = 2024
    lat_point = 51.1536 # Alice Holt
    lon_point = -0.8582
    north = lat_point + 0.125
    south = lat_point - 0.125
    west = lon_point - 0.125
    east = lon_point + 0.125

    os.makedirs(output_dir, exist_ok=True)
    download_era5_precip(start_year, end_year, north, south, west, east,
                         output_dir)
    extract_pixel_to_csv(start_year, end_year, lat_point, lon_point,
                         output_dir)
