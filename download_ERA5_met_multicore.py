#!/usr/bin/env python

"""
Download ERA5 met data using all the cores (bar one) to send off jobs to speed
things up. I think this will avoid avoid overloading the CDS API by
limiting requests per process, but let's see...

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

import os
import cdsapi
import concurrent.futures
import multiprocessing

def download_month_batch(tasks):
    for year, month, area, odir in tasks:
        monthly_fname = os.path.join(odir, f"ERA5_{year}_{month:02d}.nc")
        if os.path.exists(monthly_fname):
            print(f"Skipping {monthly_fname}, already exists.")
            continue

        print(f"Downloading {year}-{month:02d}...")

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

        try:
            client.retrieve("reanalysis-era5-land", \
                                request).download(monthly_fname)
        except Exception as e:
            print(f"Failed {year}-{month:02d}: {e}")

def chunkify(lst, n):
    # Split tasks across cores
    return [lst[i::n] for i in range(n)]

if __name__ == "__main__":

    odir = "/Users/xj21307/Desktop/ERA5_data"
    os.makedirs(odir, exist_ok=True)

    area = [51.2, -0.9, 51.2, -0.9]
    years = [2016]

    # Prepare all download tasks
    all_tasks = [(year, month, area, odir) \
                        for year in years for month in range(1, 13)]

    ncores = max(1, os.cpu_count() - 1)

    # split tasks and set running
    task_chunks = chunkify(all_tasks, ncores)
    with concurrent.futures.ProcessPoolExecutor(max_workers=ncores) as executor:
        futures = [executor.submit(download_month_batch, chunk) \
                    for chunk in task_chunks]
        concurrent.futures.wait(futures)
