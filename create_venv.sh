#!/bin/bash
python3 -m venv myenv
source myenv/bin/activate

pip3 install pip==21.3.1
pip3 install cartopy=0.20.2
pip3 install DateTime==4.3
pip3 install descartes==1.1.0
pip3 install matplotlib==3.5.1
pip3 install netCDF4==1.5.8
pip3 install numpy==1.22.0
pip3 insall pyproj==3.3.0
pip3 install scipy==1.7.3
pip3 install scikit-learn==1.0.2
pip3 install Shapely==1.8.0
pip3 install wradlib==1.13.0
pip3 install pint_xarray==0.20.0

deactivate