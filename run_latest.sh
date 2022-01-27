#!/bin/bash

# exit on first error
set -e

# activate environment
source myenv/bin/activate

# Download data from DWD`s open data server.
wget -A "*latest*" -r -np --level=2 https://opendata.dwd.de/weather/radar/sites/dx/
# wget -r --level=1 https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/1_minute/precipitation/now/

# set data path for wradlib
export WRADLIB_DATA=/home/lena/Documents/projects/radar-gauge-adjustment/opendata.dwd.de/

# processing
python code/LatestImage.py 200 1.6

# deactivate environment
deactivate