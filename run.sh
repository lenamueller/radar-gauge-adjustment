#!/bin/bash

# exit on first error
set -e

# download data from DWD`s open data server
wget -r --level=1 https://opendata.dwd.de/weather/radar/sites/dx/drs/

#!/bin/sh
# run radar adjustment
# python code/adjustment.py
# python code/visualization.py