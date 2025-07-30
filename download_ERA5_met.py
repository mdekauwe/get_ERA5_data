#!/usr/bin/env python

"""
Download ERA5 met data

https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=download

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (30.07.2025)"
__email__ = "mdekauwe@gmail.com"

import os
import cdsapi
import xarray as xr
import sys

def download_month(year, month, area, output_fname):
    client = cdsapi.Client()
    request = {
        "variable": [
            "2m_dewpoint_temperature",
            "2m_temperature",
            "surface_solar_radiation_downwards",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "surface_pressure",
            "total_precipitation",
            "leaf_area_index_high_vegetation"
        ],
        "year": str(year),
        "month": f"{month:02d}",
        "day": [f"{day:02d}" for day in range(1, 32)],
        "time": [f"{hour:02d}:00" for hour in range(24)],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": area,
    }
    client.retrieve("reanalysis-era5-land", request).download(output_fname)


if __name__ == "__main__":

    odir = "/Users/xj21307/Desktop/ERA5_data"
    if not os.path.exists(odir):
        os.makedirs(odir)

    area = [51.2, -0.9, 51.2, -0.9]

    year = 2016
    for month in range(1, 13):
        print(year, month)
        monthly_fname = os.path.join(odir, f"ERA5_{year}_{month:02d}.nc")
        download_month(year, month, area, monthly_fname)
