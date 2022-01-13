#!/bin/bash

# exit on first error
set -e

# set data path for wradlib
export WRADLIB_DATA=/home/lena/Documents/projects/radar-gauge-adjustment/opendata.dwd.de/

#!/bin/sh
# file arguments: filename, site lon, site lat, site height
python code/example_1901091200.py "raa00-dx_10488-1901091200-drs---bin" "13.769722" "51.125278" "263"
python code/example_1901091200.py "raa00-dx_10392-1901091200-pro---bin" "13.858212" "52.648667" "194"
python code/example_1901091200.py "raa00-dx_10356-1901091200-umd---bin" "11.176091" "52.160096" "185"
python code/example_1901091200.py "raa00-dx_10557-1901091200-neu---bin" "11.135034" "50.500114" "880"
python code/example_1901091200.py "raa00-dx_10780-1901091200-eis---bin" "12.402788" "49.540667" "799"