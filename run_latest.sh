#!/bin/bash

cd /home/lena/Documents/projects/radar-gauge-adjustment

# exit on first error
set -e

# Activate environment.
source myenv/bin/activate

# Download data from DWD`s open data server.
wget -A "*latest*" -r -np --level=2 https://opendata.dwd.de/weather/radar/sites/dx/

# Set data path for wradlib.
export WRADLIB_DATA=/home/lena/Documents/projects/radar-gauge-adjustment/opendata.dwd.de/

# arguments: 1) coeff a from Z-R-relation, 2) coeff b from Z-R-relation
python code/LatestImage.py 200 1.6

# Deactivate environment.
deactivate