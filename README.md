[![Repo status - Active](https://img.shields.io/badge/Repo_status-Active-00aa00)](https://)
[![GitHub issues](https://img.shields.io/github/issues/lenamueller/radar-gauge-adjustment)](https://github.com/lenamueller/radar-gauge-adjustment/issues/)
[![python - 3.10.1](https://img.shields.io/badge/python-3.10.1-ffe05c?logo=python&logoColor=4685b7)](https://)
[![field of application - meteorology, hydrology](https://img.shields.io/badge/field_of_application-meteorology%2C_hydrology-00aaff)](https://)

## radar-gauge-adjustment
Shell script for scraping data from DWD's open data server, correcting radar-specific errors and applying an adjustment for radar rainfall rates with gauge data on a 5 min or 60 min basis. 

Made as part of the lecture MHYD06 "Angewandte Meteorologie für Hydrologen" at TU Dresden.
## Usage
Create virtual environment containing all required modules with ```./create_venv.sh```.

Run latest radar image with ```./run_latest.sh```.    
Run example case with ```./run_20190109.sh```.

## Packages and Dependencies (complete)
attrs              21.4.0
certifi            2021.10.8
cftime             1.5.1.1
charset-normalizer 2.0.10
click              8.0.3
click-plugins      1.1.1
cligj              0.7.2
cloudpickle        2.0.0
cycler             0.11.0
dask               2022.1.0
DateTime           4.3
deprecation        2.1.0
descartes          1.1.0
Fiona              1.8.20
fonttools          4.28.5
fsspec             2022.1.0
GDAL               3.4.1
h5netcdf           0.13.0
h5py               3.6.0
idna               3.3
joblib             1.1.0
kiwisolver         1.3.2
locket             0.2.1
matplotlib         3.5.1
munch              2.5.0
netCDF4            1.5.8
numpy              1.22.0
packaging          21.3
pandas             1.3.5
partd              1.2.0
Pillow             9.0.0
Pint               0.18
pint-xarray        0.2.1
pip                21.3.1
pyparsing          3.0.6
pyproj             3.3.0
pyshp              2.1.3
python-dateutil    2.8.2
pytz               2021.3
PyYAML             6.0
requests           2.27.1
scikit-learn       1.0.2
scipy              1.7.3
setuptools         58.1.0
Shapely            1.8.0
six                1.16.0
threadpoolctl      3.0.0
toolz              0.11.2
urllib3            1.26.8
wradlib            1.13.0
xarray             0.20.2
xmltodict          0.12.0
zope.interface     5.4.0

## Overview
### Plot latest radar image of Germany
<img src="images/latest/RAD_composite_2022-01-27-1820.png" alt="RAD_composite_2022-01-27-1820" width="600"/>   

### Workflow (example case 09.01.2019 12:00 UTC, Eastern Germany)
#### 1. Read DX-data (Radar)
Data source: https://opendata.dwd.de/weather/radar/sites/dx/   
<img src="images/drs/radar_dx_drs_1901091200_raw.png" alt="radar_dx_drs_1901091200_raw" width="400"/>   

#### 2. Correct clutter
Apply a clutter filter with a 5x5 moving window, 6 dBZ as a threshold for difference between central pixel and surrounding pixels and 1.3 as a threshold for the ratio between pixels in a group and pixel defining its boundary (parametrization suggested by M. Gabella and R. Notarpietro, 2002).   
<img src="images/drs/radar_dx_drs_1901091200_cluttermap.png" alt="radar_dx_drs_1901091200_raw" width="400"/>
<img src="images/drs/radar_dx_drs_1901091200_noclutter.png" alt="radar_dx_drs_1901091200_noclutter" width="400"/>

### 3. Correct attenuation
Gate-to-gate algorithm to calculate the attenuation error and add it to the previous, clutter-corrected radar image to prevent an underestimation of precipitation (parametrization suggested by  Kraemer et al. 2008, Jacobi et al. 2016).   
<img src="images/drs/radar_dx_drs_1901091200_att.png" alt="radar_dx_drs_1901091200_att" width="400"/>
<img src="images/drs/radar_dx_drs_1901091200_attcorr.png" alt="radar_dx_drs_1901091200_attcorr" width="400"/>   
Averaged attenuation by distance (left) and individual attenuation for single azimuth angle 270° as an example (right):
<img src="images/drs/radar_dx_drs_1901091200_attcorr_meanbin.png" alt="radar_dx_drs_1901091200_attcorr_meanbin" width="400"/>
<img src="images/drs/radar_dx_drs_1901091200_attcorr_bin270.png" alt="radar_dx_drs_1901091200_attcorr_bin270" width="400"/>

#### 4. Derive rain depths
Apply Z-R-Relation with parametrization a=200 and b=1.6, suggested by J.S. Marshall and W. Palmer, 1948 and used by DWD for winter rain.
Integrate rain rates for 5 min (left) and 60 min (right).   
<img src="images/drs/radar_dx_drs_1901091200_raindepths5min.png" alt="radar_dx_drs_1901091200_raindepths5min" width="400"/>
<img src="images/drs/radar_dx_drs_1901091200_raindepths60min.png" alt="radar_dx_drs_1901091200_raindepths60min" width="400"/>

#### 5. Create composite and georeference
Requires step 1. to 4. for each radar site.   
The composite cointains radar sites Dresden (drs), Ummendorf (umd), Neuhaus (neu), Eisberg (eis) and Prötzel (pro) for 5 min (left) and 60 min (right) precipitation accumulation. Intersections of multiple radar fields contain the maximum value.   
<img src="images/composite_1901091200_utm5min.png" alt="composite_1901091200_utm5min" width="400"/> <img src="images/composite_1901091200_utm60min.png" alt="composite_1901091200_utm60min" width="400"/>

#### 6. Read RR-data (gauges)
Data source:  
1h-data: https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/precipitation/   
1min-data: https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/1_minute/precipitation/

#### 7. Apply adjustment methods
##### Additive adjustment with spatial differentiation
<img src="images/adjustment_add5min.png" alt="adjustment_mul5min" width="400"/><img src="images/adjustment_add60min.png" alt="adjustment_add60min" width="400"/>   
##### Multiplicative adjustment with spatial differentiation
<img src="images/adjustment_mul5min.png" alt="adjustment_mul5min" width="400"/><img src="images/adjustment_mul60min.png" alt="adjustment_mul60min" width="400"/>   
##### Multiplicative adjustment with no spatial differentiation
<img src="images/adjustment_mfb5min.png" alt="adjustment_mfb5min" width="400"/><img src="images/adjustment_mfb60min.png" alt="adjustment_mfb60min" width="400"/>   
##### Additive-multiplicative adjustment with spatial differentiation
<img src="images/adjustment_mixed5min.png" alt="adjustment_mixed5min" width="400"/><img src="images/adjustment_mixed60min.png" alt="adjustment_mixed60min" width="400"/>   

Notice: The gray dots in the maps represent gauge stations. Due to the lack of gauge station data outside of Germany the interpolation there produces artifacts and don't allow a proper interpretation of the rain field there is tricky.

#### 8. Evaluate adjustment methods
todo
