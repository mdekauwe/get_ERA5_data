#!/usr/bin/env python

"""
Merge all the downloaded ERA5 met data

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (30.07.2025)"
__email__ = "mdekauwe@gmail.com"

import os
import glob
import re
import xarray as xr
import argparse

def merge_monthly_files(nc_files, outfname, delete=False):
    sorted_files = sorted(nc_files, key=extract_year_month)

    combined = xr.open_mfdataset(sorted_files, combine='by_coords')
    combined.to_netcdf(outfname)

    if delete:
        for fname in sorted_files:
            os.remove(fname)

def extract_year_month(filename):
    match = re.search(r'ERA5_(\d{4})_(\d{2})\.nc', os.path.basename(filename))
    if match:
        year, month = int(match.group(1)), int(match.group(2))
        return year, month
    else:
        return (0, 0)  # bad file

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Merge ERA5 monthly files")
    parser.add_argument("--delete", action="store_true",
                        help="Delete original files after merging")
    args = parser.parse_args()

    fdir = "/Users/xj21307/Desktop/ERA5_data"
    nc_files = glob.glob(os.path.join(fdir, "*.nc"))
    outfname = os.path.join(fdir, "ERA5_merged.nc")
    merge_monthly_files(nc_files, outfname, delete=args.delete)
