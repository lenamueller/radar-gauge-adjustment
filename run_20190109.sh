#!/bin/bash

# Exit on first error.
set -e

# Activate virutal environment.
source myenv/bin/activate

# Set data path for wradlib.
export WRADLIB_DATA=/home/lena/Documents/projects/radar-gauge-adjustment/opendata.dwd.de/

# Download data from DWD`s open data server.
# wget -q -r --level=1 https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/1_minute/precipitation/historical/2019/
# wget -q -r --level=1 https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/precipitation/historical/

#!/bin/sh
# Run radar postprocessing and plotting. Arguments is time in minutes. Code works for 5 and 60 minutes.
# python code/PlotCorrection.py "raa00-dx_10488-1901091200-drs---bin" 60
# python code/PlotCorrection.py "raa00-dx_10392-1901091200-pro---bin" 60
# python code/PlotCorrection.py "raa00-dx_10356-1901091200-umd---bin" 60
# python code/PlotCorrection.py "raa00-dx_10557-1901091200-neu---bin" 60
# python code/PlotCorrection.py "raa00-dx_10780-1901091200-eis---bin" 60
python code/PlotComposite.py 5

# Deactivate virtual env.
deactivate