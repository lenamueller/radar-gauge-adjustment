#!/bin/bash

# exit on first error
set -e

# activate environment
source myenv/bin/activate

# download data from DWD`s open data server
wget -r --level=1 https://opendata.dwd.de/weather/radar/sites/dx/drs/
wget -r --level=1 https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/1_minute/precipitation/now/
wget -r --level=1 https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/1_minute/precipitation/historical/2019/1minutenwerte_nieder_01048_20190101_20190131_hist.zip
wget -r --level=1 https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/precipitation/historical/

# set data path for wradlib
export WRADLIB_DATA=/home/lena/Documents/projects/radar-gauge-adjustment/opendata.dwd.de/

# processing
# todo

# deactivate environment
deactivate