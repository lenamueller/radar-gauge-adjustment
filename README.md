[![Repo status - Active](https://img.shields.io/badge/Repo_status-Active-00aa00)](https://)
[![GitHub issues](https://img.shields.io/github/issues/lenamueller/radar-gauge-adjustment)](https://github.com/lenamueller/radar-gauge-adjustment/issues/)
[![python - 3.10.1](https://img.shields.io/badge/python-3.10.1-ffe05c?logo=python&logoColor=4685b7)](https://)
[![field of application - meteorology, hydrology](https://img.shields.io/badge/field_of_application-meteorology%2C_hydrology-00aaff)](https://)

## radar-gauge-adjustment
Shell script for scraping data from DWD's open data server and applying an adjustment for radar rainfall rates with gauge data. 

Run example case with ```source run_sample.sh```.   
Run latest radar images with ```source run.sh``` (todo).


## Packages and Dependencies
pip 21.3.1
cartopy 0.20.2
DateTime 4.3
matplotlib 3.5.1
netCDF4 1.5.8
numpy 1.22.0
pandas 1.3.5
scipy 1.7.3
wradlib 1.13.0
pint_xarray

## Workflow (test case 09.01.2019 12:00 UTC)
### 1. Read DX-data 
Data source: https://opendata.dwd.de/weather/radar/sites/dx/   
<img src="images/radar_dx_drs_1901091200_raw.png" alt="radar_dx_drs_1901091200_raw" width="400"/>

### 2. Correct clutter
Clutter identification, removal and data interpolation (algorithm by Gabella et al. 2002).
<img src="images/radar_dx_drs_1901091200_cluttermap.png" alt="radar_dx_drs_1901091200_raw" width="400"/>
<img src="images/radar_dx_drs_1901091200_noclutter.png" alt="radar_dx_drs_1901091200_noclutter" width="400"/>

### 3. Correct attenuation
Calculate integrated attenuation for each bin (Kraemer et al. 2008, Jacobi et al. 2016).   
<img src="images/radar_dx_drs_1901091200_att.png" alt="radar_dx_drs_1901091200_att" width="400"/>
<img src="images/radar_dx_drs_1901091200_attcorr.png" alt="radar_dx_drs_1901091200_attcorr" width="400"/>

#### Averaged attenuation:   
<img src="images/radar_dx_drs_1901091200_attcorr_meanbin.png" alt="radar_dx_drs_1901091200_attcorr_meanbin" width="400"/>

#### Individual attenuation for single azimuth angles (examples):   
<img src="images/radar_dx_drs_1901091200_attcorr_bin90.png" alt="radar_dx_drs_1901091200_attcorr_bin90" width="400"/> <img src="images/radar_dx_drs_1901091200_attcorr_bin270.png" alt="radar_dx_drs_1901091200_attcorr_bin270" width="400"/>

### 4. Calculate rain depths
Apply ZR-Relation with coefficients a=200 and b=1.6. Integrate rain rates for 60min.   
<img src="images/radar_dx_drs_1901091200_raindepths.png" alt="radar_dx_drs_1901091200_raindepths" width="400"/>

### 5. Create composite and georeference
Contains 60min rain accumulation for radar sites Dresden (drs), Ummendorf (umd), Neuhaus (neu), Eisberg (eis) and Prötzel (pro).   
Requires step 1. to 4. for each radar site.   
<img src="images/composite_1901091200_utm60min.png" alt="composite_1901091200_utm60min" width="500"/>

### 6. Read gauge-data 
Data source:  
1h-data: https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/precipitation/   
1min-data: https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/1_minute/precipitation/

### 7. Apply RADAR-gauge adjustment methods
<img src="images/adjustment_add.png" alt="adjustment_add" width="400"/> <img src="images/adjustment_mfb.png" alt="adjustment_mfb" width="400"/>
<img src="images/adjustment_mul.png" alt="adjustment_mul" width="400"/> <img src="images/adjustment_mixed.png" alt="adjustment_mixed" width="400"/>

### 8. Evaluation
<img src="images/adjustment_eval.png" alt="adjustment_eval" width="500"/>
