[![Repo status - Active](https://img.shields.io/badge/Repo_status-Active-00aa00)](https://)
[![GitHub issues](https://img.shields.io/github/issues/lenamueller/radar-gauge-adjustment)](https://github.com/lenamueller/radar-gauge-adjustment/issues/)
[![python - 3.10.1](https://img.shields.io/badge/python-3.10.1-ffe05c?logo=python&logoColor=4685b7)](https://)
[![field of application - meteorology, hydrology](https://img.shields.io/badge/field_of_application-meteorology%2C_hydrology-00aaff)](https://)

## radar-gauge-adjustment
Shell script for scraping data from DWD's open data server and applying an adjustment for radar rainfall rates with gauge data. 

Create virtual environment with all required modules with  ```./create_venv..sh```.    
Run example case with ```./run_sample.sh```.   
Run latest radar images with ```./source run.sh``` (todo).


## Packages and Dependencies
pip 21.3.1
cartopy 0.20.2
DateTime 4.3
matplotlib 3.5.1
netCDF4 1.5.8
numpy 1.22.0
pandas 1.3.5
scikit-learn 1.0.2
scipy 1.7.3
wradlib 1.13.0
pint_xarray

## Workflow (test case 09.01.2019 12:00 UTC)
### 1. Read DX-data (Radar)
Data source: https://opendata.dwd.de/weather/radar/sites/dx/   
<img src="images/drs/radar_dx_drs_1901091200_raw.png" alt="radar_dx_drs_1901091200_raw" width="400"/>

### 2. Correct clutter
Clutter identification, removal and data interpolation (algorithm by Gabella et al. 2002).
<img src="images/drs/radar_dx_drs_1901091200_cluttermap.png" alt="radar_dx_drs_1901091200_raw" width="400"/>
<img src="images/drs/radar_dx_drs_1901091200_noclutter.png" alt="radar_dx_drs_1901091200_noclutter" width="400"/>

### 3. Correct attenuation
Calculate integrated attenuation for each bin (Kraemer et al. 2008, Jacobi et al. 2016).   
Upper left: attenuation error, upper right: radar image after attenuation correction, lower left: averaged attenuation by distance, lower right: individual attenuation for single azimuth angle (e.g. 270°)   
<img src="images/drs/radar_dx_drs_1901091200_att.png" alt="radar_dx_drs_1901091200_att" width="400"/>
<img src="images/drs/radar_dx_drs_1901091200_attcorr.png" alt="radar_dx_drs_1901091200_attcorr" width="400"/>
<img src="images/drs/radar_dx_drs_1901091200_attcorr_meanbin.png" alt="radar_dx_drs_1901091200_attcorr_meanbin" width="400"/>
<img src="images/drs/radar_dx_drs_1901091200_attcorr_bin270.png" alt="radar_dx_drs_1901091200_attcorr_bin270" width="400"/>

### 4. Derive rain depths
Apply Z-R-Relation (coefficients a=200 and b=1.6) and integrate rain rates for 60 min.   
<img src="images/drs/radar_dx_drs_1901091200_raindepths.png" alt="radar_dx_drs_1901091200_raindepths" width="400"/>

### 5. Create composite and georeference
Requires step 1. to 4. for each radar site.   
Contains 60min rain accumulation for radar sites Dresden (drs), Ummendorf (umd), Neuhaus (neu), Eisberg (eis) and Prötzel (pro).   
<img src="images/composite_1901091200_utm60min.png" alt="composite_1901091200_utm60min" width="400"/>

### 6. Read RR-data (gauges)
Data source:  
1h-data: https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/precipitation/   
1min-data: https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/1_minute/precipitation/

### 7. Apply adjustment methods
#### hourly adjustment
<img src="images/adjustment_add60min.png" alt="adjustment_add60min" width="400"/> <img src="images/adjustment_mfb60min.png" alt="adjustment_mfb60min" width="400"/>
<img src="images/adjustment_mul60min.png" alt="adjustment_mul60min" width="400"/> <img src="images/adjustment_mixed60min.png" alt="adjustment_mixed60min" width="400"/>

#### 5min adjustment
todo

### 8. Evaluate adjustment methods
todo
