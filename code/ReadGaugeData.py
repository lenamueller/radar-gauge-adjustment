import os
import datetime
import numpy as np
import scipy as sp
from pyproj import Proj
import zipfile


myProj = Proj("+proj=utm +zone=33 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

def read_gauges_1min(gaugelist, xgrid, ygrid, path_to_data):
    gaugedata = {"id": [], "prec_mm": []}
    files = [_ for _ in os.listdir(path_to_data) if _.endswith(r".zip")]
    # files = [f for f in os.listdir(path_to_data) if os.path.isfile(os.path.join(path_to_data, f))]
    
    # Unzip files of interest.
    for file in files:
        date_start = datetime.datetime.strptime(file[27:35], '%Y%m%d')
        date_end = datetime.datetime.strptime(file[36:44], '%Y%m%d')
        date_of_interest = datetime.datetime(year=2019, month=1, day=9)
        if (date_start < date_of_interest < date_end) and (file[21:26] in gaugelist):
            with zipfile.ZipFile(path_to_data+file, 'r') as zip_ref:
                zip_ref.extractall(path_to_data)

    # Go through extracted data files and fill gauge dict with id and precipitation.    
    files_extracted = [_ for _ in os.listdir(path_to_data) if _.endswith(r".txt")]
    for file in files_extracted:
        with open(path_to_data+file) as f:
            lines = f.readlines()[1:]
            p_list = []
            for line in lines:
                line_split = [x.strip() for x in line.split(';')]
                if line_split[1] in ["201901091201","201901091202","201901091203","201901091204","201901091205"]:
                    p_list.append(float(line_split[4]))
            gaugedata["id"].append(line_split[0].zfill(5))                        
            gaugedata["prec_mm"].append(np.round(sum(p_list),3))

    # Add easting, northing and elevation for given id's.
    num_gauges = len(gaugedata["id"])
    gaugedata["easting"] = [0 for _ in range(num_gauges)]
    gaugedata["northing"] = [0 for _ in range(num_gauges)]
    gaugedata["elevation"] = [0 for _ in range(num_gauges)]

    with open("opendata.dwd.de/example_data/RR_Stundenwerte_Beschreibung_Stationen_neu.txt", "w") as f2:
        with open("opendata.dwd.de/example_data/RR_Stundenwerte_Beschreibung_Stationen.txt", "r", errors="replace") as f:
            lines = f.readlines()[2:] # Pass first two lines.
            for line in lines: 
                line = ' '.join(line.split()) # Reduce whitespaces.
                f2.write(line+"\n") 
                line = [x.strip() for x in line.split(' ')]
                gauge_id = line[0]
                for i in range(len(gaugedata["id"])): # Go through gauge dict.
                    if gaugedata["id"][i] == gauge_id:
                        east, north = myProj(line[5], line[4])                   
                        gaugedata["easting"][i] = min(xgrid, key=lambda x:abs(x-east)) # get closest pixel in xgrid
                        gaugedata["northing"][i] = min(ygrid, key=lambda x:abs(x-north)) # get closest pixel in ygrid
                        gaugedata["elevation"][i] = line[3]
                        
    return gaugedata


def read_gauges_60min(gaugelist, xgrid, ygrid, path_to_data="opendata.dwd.de/example_data/hourly_data/"):
    """Create gauge dict from gauge list and data input files."""
    gaugedata = {"id": [], "prec_mm": []}
    files = [f for f in os.listdir(path_to_data) if os.path.isfile(os.path.join(path_to_data, f))]
    
    # Go through data files and fill gauge dict with id and precipitation.
    for file in files:
        date_start = datetime.datetime.strptime(file[18:26], '%Y%m%d')
        date_end = datetime.datetime.strptime(file[27:35], '%Y%m%d')
        date_of_interest = datetime.datetime(year=2019, month=1, day=9)
        if date_start < date_of_interest < date_end:
            gauge_id = file[36:41]
            with open(path_to_data+file) as f:
                for line in f:
                    line_split = [x.strip() for x in line.split(';')]
                    if "2019010912" in line_split[1]:
                        g_id = line_split[0].zfill(5)
                        if g_id in gaugelist:
                            gaugedata["id"].append(g_id)
                            gaugedata["prec_mm"].append(float(line_split[3]))

    # Add easting, northing and elevation for given id's.
    num_gauges = len(gaugedata["id"])
    gaugedata["easting"] = [0 for _ in range(num_gauges)]
    gaugedata["northing"] = [0 for _ in range(num_gauges)]
    gaugedata["elevation"] = [0 for _ in range(num_gauges)]

    with open("opendata.dwd.de/example_data/RR_Stundenwerte_Beschreibung_Stationen_neu.txt", "w") as f2:
        with open("opendata.dwd.de/example_data/RR_Stundenwerte_Beschreibung_Stationen.txt", "r", errors="replace") as f:
            lines = f.readlines()[2:] # Pass first two lines.
            for line in lines: 
                line = ' '.join(line.split()) # Reduce whitespaces.
                f2.write(line+"\n") 
                line = [x.strip() for x in line.split(' ')]
                gauge_id = line[0]
                for i in range(len(gaugedata["id"])): # Go through gauge dict.
                    if gaugedata["id"][i] == gauge_id:
                        east, north = myProj(line[5], line[4])                   
                        gaugedata["easting"][i] = min(xgrid, key=lambda x:abs(x-east)) # get closest pixel in xgrid
                        gaugedata["northing"][i] = min(ygrid, key=lambda x:abs(x-north)) # get closest pixel in ygrid
                        gaugedata["elevation"][i] = line[3]
    
    return gaugedata


def gaugearray(gaugedict, xgrid, ygrid, method="cubic"):
    """Create gauge array from gauge dict. Interpolate gauge array."""
    gauge_array = np.empty((700,700))
    gauge_stations = np.zeros((700,700))
    gauge_array[:] = np.NaN
    gauge_indices = []
    for g in range(len(gaugedict["id"])):
        east = gaugedict["easting"][g]
        north = gaugedict["northing"][g]
        prec = gaugedict["prec_mm"][g]
        x_i = list(xgrid).index(east)
        y_i = list(ygrid).index(north)
        gauge_indices.append([y_i, x_i])
        gauge_array[y_i][x_i] = prec
        gauge_stations[y_i][x_i] = 1
    # Interpolation.
    all_indices = ([[x, y] for x in range(700) for y in range(700)])
    gauge_array_ipol = sp.interpolate.griddata(points = gauge_indices, values = gaugedict["prec_mm"], xi = all_indices, method=method)
    gauge_array_ipol = gauge_array_ipol.reshape((700,700))
    
    return gauge_array, gauge_array_ipol, gauge_stations