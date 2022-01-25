#!/bin/bash

# exit on first error
set -e

# activate virutal environment
source myenv/bin/activate

# set data path for wradlib
export WRADLIB_DATA=/home/lena/Documents/projects/radar-gauge-adjustment/opendata.dwd.de/

# download data from DWD`s open data server
# wget -r --level=1 https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/1_minute/precipitation/historical/2019/

#!/bin/sh
# Plot raw data, clutter correction, attenuation correction, rain depths.
python code/PlotCorrection.py "raa00-dx_10488-1901091200-drs---bin" 60
python code/PlotCorrection.py "raa00-dx_10392-1901091200-pro---bin" 60
python code/PlotCorrection.py "raa00-dx_10356-1901091200-umd---bin" 60
python code/PlotCorrection.py "raa00-dx_10557-1901091200-neu---bin" 60
python code/PlotCorrection.py "raa00-dx_10780-1901091200-eis---bin" 60

# Plot composite, adjustment methods and evaluation.
python code/PlotComposite.py 60

# deactivate virtual env.
deactivate