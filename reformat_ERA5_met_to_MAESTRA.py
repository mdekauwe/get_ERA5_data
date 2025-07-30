#!/usr/bin/env python

"""
Reformat the ERA5 met file for use with the MAESTRA model

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (08.07.2025)"
__email__ = "mdekauwe@gmail.com"

import os
import xarray as xr
import sys
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def main(in_fname, out_fname):

    ds = xr.open_dataset(in_fname)

    time_var = ds["valid_time"]
    base_time = datetime(1970, 1, 1)
    times = np.array(time_var.values).astype('datetime64[s]').astype(datetime)

    start_date_fmt = times[0].strftime("%d/%m/%y")
    end_date_fmt = times[-1].strftime("%d/%m/%y")

    center_lat = float(ds.latitude.mean().values)

    # fix for era5 format
    raw_lon = float(ds.longitude.mean().values)
    center_lon = normalise_longitude(raw_lon)

    lat_deg, lat_min, lat_sec = decimal_to_dms(center_lat)
    lon_deg, lon_min, lon_sec = decimal_to_dms(center_lon)
    lat_hem = get_hemisphere(center_lat, 'lat')
    lon_hem = get_hemisphere(center_lon, 'lon')

    times = np.array(ds.valid_time.values).astype('datetime64[s]').astype(datetime)
    doy = [dt.timetuple().tm_yday for dt in times]
    times = ds['valid_time'].values

    tair = ds['t2m'][:, 0, 0].values - 273.15
    dew = ds['d2m'][:, 0, 0].values
    sp = ds['sp'][:, 0, 0].values
    rh = relative_humidity(ds['t2m'][:, 0, 0].values, dew)
    tp_vals = ds['tp'][:, 0, 0].values * 1000.0  # m to mm, cumulative values
    ppt = np.diff(tp_vals, prepend=tp_vals[0])
    ppt = np.clip(ppt, 0, None)  # no negative precipitation
    u10 = ds['u10'][:, 0, 0].values
    v10 = ds['v10'][:, 0, 0].values
    wind = np.sqrt(u10**2 + v10**2)
    ssrd_vals = ds['ssrd'][:, 0, 0].values
    # Shift values to calculate differences between time steps
    rad = np.diff(ssrd_vals, prepend=ssrd_vals[0]) / 3600
    rad = np.clip(rad, 0, None)  # set any negative values to zero

    press = ds['sp'][:, 0, 0].values
    par = rad * 2.3  # umol m-2 s-1


    df = pd.DataFrame({
        'DOY': doy,
        'TAIR': tair,
        'RH%': rh,
        'PPT': ppt,
        'WIND': wind,
        'RAD': rad,
        'PRESS': press,
        'PAR': par
    })

    with open(out_fname, "w") as f:
        f.write("&environ\n")
        f.write("difsky = 0.0\n")
        f.write("ca = 420\n")
        f.write("/\n\n")

        f.write("&latlong\n")
        f.write(f"lat={lat_deg} {lat_min} {lat_sec}\n")
        f.write(f"long={lon_deg} {lon_min} {lon_sec}\n")
        f.write("tzlong=0\n")
        f.write(f"lonhem='{lon_hem}'\n")
        f.write(f"lathem='{lat_hem}'\n")
        f.write("/\n\n")

        f.write("&metformat\n")
        f.write("dayorhr=1\n")
        f.write("khrsperday=24\n")
        f.write("nocolumns=8\n")
        f.write(f"startdate='{start_date_fmt}'\n")
        f.write(f"enddate='{end_date_fmt}'\n")
        f.write("columns=\t'DOY'\t'TAIR'\t'RH%'\t'PPT'\t'WIND'\t'RAD'\t'PRESS'\n'PAR'\n")
        f.write("/\n\n")
        f.write("DATA STARTS\n")
        df.to_csv(f, index=False, sep="\t", header=False, float_format="%.6f")

def decimal_to_dms(decimal):
    degrees = int(abs(decimal))
    minutes = int((abs(decimal) - degrees) * 60)
    seconds = int(round(((abs(decimal) - degrees) * 60 - minutes) * 60))

    return degrees, minutes, seconds

def get_hemisphere(val, axis):
    if axis == 'lat':
        return 'N' if val >= 0 else 'S'
    elif axis == 'lon':
        return 'E' if val >= 0 else 'W'

def normalise_longitude(lon):
    # Convert longitude from 0–360 to -180–180
    return lon - 360 if lon > 180 else lon

def saturation_vapor_pressure(T):
    return 6.112 * np.exp((17.67 * T) / (T + 243.5)) # deg Cs

def relative_humidity(tair_k, dew_k):
    tair_c = tair_k - 273.15
    dew_c = dew_k - 273.15
    es = saturation_vapor_pressure(tair_c)
    ea = saturation_vapor_pressure(dew_c)
    rh = (ea / es) * 100.0

    return np.clip(rh, 0, 100)


if __name__ == "__main__":

    in_fname = "/Users/xj21307/Desktop/ERA5_data/ERA5_merged.nc"
    out_fname = "/Users/xj21307/Desktop/ERA5_data/maestra_era5_met_data_merged.csv"

    main(in_fname, out_fname)
