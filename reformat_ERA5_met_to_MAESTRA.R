library(ncdf4)
library(tidyverse)

get_dms <- function(decimal) {
  degrees <- floor(abs(decimal))
  minutes <- floor((abs(decimal) - degrees) * 60)
  seconds <- round((((abs(decimal) - degrees) * 60) - minutes) * 60)
  c(degrees, minutes, seconds)
}

get_hemisphere <- function(val, axis) {
  if (axis == "lat") {
    ifelse(val >= 0, "N", "S")
  } else {
    ifelse(val >= 0, "E", "W")
  }
}

decimal_to_dms <- function(val, axis) {
  list(
    dms = get_dms(val),
    hem = get_hemisphere(val, axis)
  )
}

svp <- function(T) {
  6.112 * exp((17.67 * T) / (T + 243.5))
}




in_fname <- "/Users/xj21307/Desktop/era5_met_data_may_2016.nc"
out_fname <- "/Users/xj21307/Desktop/maestra_era5_met_data_may_2016_fromR.csv"

nc <- nc_open(in_fname)

time_sec <- ncvar_get(nc, "valid_time")
time <- as.POSIXct(time_sec, origin = "1970-01-01", tz = "UTC")
doy <- lubridate::yday(time)

lat <- ncvar_get(nc, "latitude")
lon <- ncvar_get(nc, "longitude")
lon <- ifelse(lon > 180, lon - 360, lon)

lat_dms <- decimal_to_dms(lat, "lat")
lon_dms <- decimal_to_dms(lon, "lon")

tair <- ncvar_get(nc, "t2m") - 273.15
dew <- ncvar_get(nc, "d2m")
ppt_cum <- ncvar_get(nc, "tp") * 1000.0  # cumulative precipitation in mm
ppt <- diff(c(ppt_cum[1], ppt_cum))      # hourly incremental precipitation
ppt[ppt < 0] <- 0                        # clip negatives to zero
u10 <- ncvar_get(nc, "u10")
v10 <- ncvar_get(nc, "v10")
wind <- sqrt(u10^2 + v10^2)
ssrd <- ncvar_get(nc, "ssrd")
rad <- diff(c(ssrd[1], ssrd)) / 3600  # Convert accumulated J/m2 → W/m2
rad[rad < 0] <- 0                     # Clip negative radiation
par <- rad * 2.3
press <- ncvar_get(nc, "sp")

# Relative humidity
tair_c <- tair
dew_c <- dew - 273.15
ea <- svp(dew_c)
es <- svp(tair_c)
rh <- pmin(pmax((ea / es) * 100, 0), 100)

df <- tibble(
  DOY = doy,
  TAIR = tair,
  `RH%` = rh,
  PPT = ppt,
  WIND = wind,
  RAD = rad,
  PRESS = press,
  PAR = par
)

start_date_fmt <- format(min(time), "%d/%m/%y")
end_date_fmt <- format(max(time), "%d/%m/%y")

# Write header
sink(out_fname)
cat("&environ\n")
cat("difsky = 0.0\n")
cat("ca = 420\n")
cat("/\n\n")

cat("&latlong\n")
cat(sprintf("lat=%d %d %d\n", lat_dms$dms[1], lat_dms$dms[2], lat_dms$dms[3]))
cat(sprintf("long=%d %d %d\n", lon_dms$dms[1], lon_dms$dms[2], lon_dms$dms[3]))
cat("tzlong=0\n")
cat(sprintf("lonhem='%s'\n", lon_dms$hem))
cat(sprintf("lathem='%s'\n", lat_dms$hem))
cat("/\n\n")

cat("&metformat\n")
cat("dayorhr=1\n")
cat("khrsperday=24\n")
cat("nocolumns=8\n")
cat(sprintf("startdate='%s'\n", start_date_fmt))
cat(sprintf("enddate='%s'\n", end_date_fmt))
cat("columns=\t'DOY'\t'TAIR'\t'RH%'\t'PPT'\t'WIND'\t'RAD'\t'PRESS'\n'PAR'\n")
cat("/\n\n")
cat("DATA STARTS\n")
sink()

write.table(round(df, 6), file = out_fname, append = TRUE, sep = "\t",
            col.names = FALSE, row.names = FALSE, quote = FALSE,
            na = "NaN")
nc_close(nc)
