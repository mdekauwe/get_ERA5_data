#!/usr/bin/env python

"""
Download ERA5 met data

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (08.07.2025)"
__email__ = "mdekauwe@gmail.com"

import os
import cdsapi
import xarray as xr
import sys

def main(year, location, outfname):

    for month in range(1, 13):
        monthly_fname = f"ERA5_{year}_{month:02d}.nc"
        download_month(year, month, location, monthly_fname)

    merge_monthly_files(year, outfname)

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

def merge_monthly_files(year, outfname):
    files = [f"ERA5_{year}_{month:02d}.nc" for month in range(1, 13)]
    datasets = [xr.open_dataset(f) for f in files]
    combined = xr.concat(datasets, dim="time")
    combined.to_netcdf(outfname)

    # Clean up individual files
    for ds, fname in zip(datasets, files):
        ds.close()
        os.remove(fname)


if __name__ == "__main__":

    ofname = "/Users/xj21307/Desktop/era5_met_data.nc"
    year = 2016
    location = [51.1, 0.85, 49.6, 0.9]  # N, W, S, E
    main(year, location, ofname)
