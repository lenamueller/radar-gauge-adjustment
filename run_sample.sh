#!/bin/bash

# exit on first error
set -e

# activate virutal environment
source myenv/bin/activate

# set data path for wradlib
export WRADLIB_DATA=/home/lena/Documents/projects/radar-gauge-adjustment/opendata.dwd.de/

#!/bin/sh
# file arguments: filename, site lon, site lat, site height
python code/example_1901091200.py

# deactivate virtual env.
deactivate
