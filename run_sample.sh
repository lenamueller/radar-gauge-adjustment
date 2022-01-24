#!/bin/bash

# exit on first error
set -e

# activate virutal environment
source myenv/bin/activate

# set data path for wradlib
export WRADLIB_DATA=/home/lena/Documents/projects/radar-gauge-adjustment/opendata.dwd.de/

#!/bin/sh
# Plot raw data, clutter correction, attenuation correction, rain depths.
python code/PlotCorrection.py "raa00-dx_10488-1901091200-drs---bin" 3600
python code/PlotCorrection.py "raa00-dx_10392-1901091200-pro---bin" 3600
python code/PlotCorrection.py "raa00-dx_10356-1901091200-umd---bin" 3600
python code/PlotCorrection.py "raa00-dx_10557-1901091200-neu---bin" 3600
python code/PlotCorrection.py "raa00-dx_10780-1901091200-eis---bin" 3600

# Plot composite, adjustment methods and evaluation.




# deactivate virtual env.
deactivate