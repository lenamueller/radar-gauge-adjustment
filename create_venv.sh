#!/bin/bash
python3 -m venv myenv
source myenv/bin/activate

pip3 install pip==21.3.1
pip3 install DateTime==4.3
pip3 install matplotlib==3.5.1
pip3 install netCDF4==1.5.8
pip3 install numpy==1.22.0
pip3 install pandas==1.3.5
pip3 install scipy==1.7.3
pip3 install wradlib==1.13.0

deactivate