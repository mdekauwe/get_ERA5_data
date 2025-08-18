#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma, norm


def compute_spi_from_roll(roll_sum):
    """Compute SPI from precomputed rolling sums using gamma fit."""
    valid = roll_sum.dropna()
    spi_values = pd.Series(index=roll_sum.index, dtype=float)

    if len(valid) >= 5:
        fit_alpha, fit_loc, fit_beta = gamma.fit(valid, floc=0)
        cdf = gamma.cdf(valid, a=fit_alpha, loc=fit_loc, scale=fit_beta)
        spi_values[valid.index] = norm.ppf(cdf)

    return spi_values


if __name__ == "__main__":

    csv_file = ("/Users/xj21307/Desktop/ERA5_precip/"
                "ERA5_precip_51.1536_-0.8582.csv")
    output_plot = "/Users/xj21307/Desktop/spi_plot.png"

    # load monthly precipitation
    df = pd.read_csv(csv_file, parse_dates=['time'])
    df = df.sort_values('time')
    df.set_index('time', inplace=True)
    precip = df['rain_mm']

    # precompute rolling sums
    scales = [1, 3, 6]
    roll_sums = {s: precip.rolling(window=s, min_periods=s).sum()
                 for s in scales}

    # calculate spi
    df_spi = pd.DataFrame(index=df.index)
    for s in scales:
        df_spi[f'spi_{s}'] = compute_spi_from_roll(roll_sums[s])

    df_spi.index = pd.to_datetime(df_spi.index)

    # plot
    plt.figure(figsize=(12, 6))

    # shaded drought categories
    plt.axhspan(-1.99, -1.5, color='#56B4E9', alpha=0.5, label="_nolegend_")
    plt.axhspan(-2.5, -2.0, color='#CC79A7', alpha=0.7, label="_nolegend_")

    # vertical highlight for 2022
    plt.axvspan(pd.Timestamp('2022-01-01'), pd.Timestamp('2022-12-31'),
                color='#E69F00', alpha=0.4, label='2022')

    # plot all SPI series
    #plt.plot(df_spi.index, df_spi['spi_1'], label='SPI-1', color="#009E73")
    plt.plot(df_spi.index, df_spi['spi_3'], label='SPI-3', color="#0072B2")
    plt.plot(df_spi.index, df_spi['spi_6'], label='SPI-6', color="#D55E00")
    plt.axhline(0, color='k', linestyle='--', linewidth=0.8)

    plt.xlabel('year')
    plt.ylabel('standardized precipitation index (-)')
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(output_plot, dpi=300)
    plt.show()

    # print monthly SPI to screen
    df_spi['year'] = df_spi.index.year
    df_spi['month'] = df_spi.index.month

    for year, group in df_spi.groupby('year'):
        print(f"\nYear {year}:")
        for _, row in group.iterrows():
            month_name = row.name.strftime('%b')
            print(f"  {month_name}: SPI-1 = {row['spi_1']:.2f}, "
                  f"SPI-3 = {row['spi_3']:.2f}, SPI-6 = {row['spi_6']:.2f}")
