import sys
from os import listdir
from os.path import isfile, join
import datetime
import zipfile
import pandas as pd
import numpy as np
import wradlib as wrl
import matplotlib.pylab as pl
import wradlib.adjust as adjust
import wradlib.verify as verify
import wradlib.util as util
from pyproj import Proj

from colorbar import cm
from func import get_depths


# Projections
utm = wrl.georef.epsg_to_osr(32633)
# wgs84 = wrl.georef.epsg_to_osr(4326)

# Define filenames.
filename_drs = "raa00-dx_10488-1901091200-drs---bin"
filename_pro = "raa00-dx_10392-1901091200-pro---bin"
filename_umd = "raa00-dx_10356-1901091200-umd---bin"
filename_neu = "raa00-dx_10557-1901091200-neu---bin"
filename_eis = "raa00-dx_10780-1901091200-eis---bin"

# Define radar site location (lon, lat, elev).
radar_location_drs = (13.769722, 51.125278, 263)
radar_location_pro = (13.858212, 52.648667, 194)
radar_location_umd = (11.176091, 52.160096, 185)
radar_location_neu = (11.135034, 50.500114, 880)
radar_location_eis = (12.402788, 49.540667, 799)

# polar coords
elevation = 0.5 # in degree
azimuths = np.arange(0,360) # in degrees
ranges = np.arange(0, 128000., 1000.) # in meters
polargrid = np.meshgrid(ranges, azimuths)

# new grid
xgrid = np.linspace(-50000, 650000, 700)
ygrid = np.linspace(5350000, 6050000, 700)
grid_xy = np.meshgrid(xgrid, ygrid)
grid_xy = np.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose()

def polar_to_utm(filename, radar_location_latlon):
    """
    Read data and calculate rain depths. 
    Convert polar coordinates in xyz cartesian coordinates. 
    Reproject the cartesian coordinates into UTM Zone 33N and grid data.
    """
    data = get_depths(filename)
    coords, rad = wrl.georef.spherical_to_xyz(polargrid[0], polargrid[1], elevation, radar_location_latlon)
    utm_coords = wrl.georef.reproject(coords, projection_source=rad,projection_target=utm)
    x = utm_coords[..., 0]
    y = utm_coords[..., 1]
    xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)
    gridded = wrl.comp.togrid(xy, grid_xy, 128000., np.array([x.mean(), y.mean()]), data.ravel(), wrl.ipol.Nearest)
    gridded = gridded.reshape((len(xgrid), len(ygrid)))    
    return gridded


def blending_radar_domains(domain, gridded_data):
    """Change nan's to zeros. Choose element wise maximum."""
    return np.maximum(domain, np.nan_to_num(gridded_data))

gridded_drs = polar_to_utm(filename_drs, radar_location_drs)
gridded_eis = polar_to_utm(filename_eis, radar_location_eis)
gridded_umd = polar_to_utm(filename_umd, radar_location_umd)
gridded_pro = polar_to_utm(filename_pro, radar_location_pro)
gridded_neu = polar_to_utm(filename_neu, radar_location_neu)

# Fix wrong pixels in umd-radar domain
for row in range(700):
    for col in range(700):
        if 430 <= row <=439 and 286 <= col <= 303:
            gridded_umd[row][col]=0

# Merge radar domains.            
domain = blending_radar_domains(np.zeros((700,700)), gridded_drs)
domain = blending_radar_domains(domain, gridded_eis)
domain = blending_radar_domains(domain, gridded_pro)
domain = blending_radar_domains(domain, gridded_umd)
domain = blending_radar_domains(domain, gridded_neu)
radar = domain

# Save grid information to files.
np.savetxt("geodata/xgrid.txt", xgrid, fmt = "%.4f")
np.savetxt("geodata/ygrid.txt", ygrid, fmt = "%.4f")
np.savetxt("geodata/griddata_5min.txt", radar, fmt = "%.4f")

# Plot composite.
fig = pl.figure(figsize=(10,8))
ax = pl.subplot(111, aspect="equal") # aspect=111/71
pm = pl.pcolormesh(xgrid, ygrid, radar, cmap=cm, vmax=0.35)
cbar = pl.colorbar(pm)
cbar.set_label("5 min - rain depths (mm)", fontsize=12)
ax.ticklabel_format(useOffset=False, style='plain')
pl.xlabel("Easting (m)")
pl.ylabel("Northing (m)")
# pl.xlim(min(xgrid), max(xgrid))
# pl.ylim(min(ygrid), max(ygrid))
pl.xlim(50000, 600000)
pl.ylim(min(ygrid), 6000000)
pl.grid(lw=0.5)
pl.xlabel("Easting", fontsize=12)
pl.ylabel("Northing", fontsize=12)
pl.title('09-01-2019 12:00 UTC\nDWD RADAR composite\nUTM zone 33N (EPSG 32633)', fontsize=12)
pl.savefig(f"images/composite_{filename_drs[15:25]}_utm5min", dpi=600)


def latlon_to_utm33N(lon, lat):
    """Convert lat/lon to UTM Zone 33/ WGS84 coords."""
    myProj = Proj("+proj=utm +zone=33 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    east, north = myProj(lon, lat)
    return east, north

# Read gauge data

# Gauges of interest
gauges_in_domain = ['00029', '00046', '00053', '00073', '00087', '00096', '00103', '00118', '00124', '00131', '00151', '00152', '00164', '00191', '00198', '00213', '00222', '00227', '00240', '00246', '00282', '00287', '00294', '00303', '00314', '00320', '00336', '00359', '00360', '00378', '00379', '00399', '00400', '00403', '00410', '00420', '00427', '00430', '00433', '00445', '00504', '00505', '00542', '00550', '00551', '00567', '00589', '00622', '00630', '00633', '00656', '00662', '00714', '00721', '00735', '00753', '00775', '00797', '00807', '00812', '00814', '00815', '00840', '00848', '00853', '00863', '00867', '00874', '00880', '00885', '00896', '00962', '00966', '00970', '00974', '00991', '01001', '01039', '01048', '01050', '01051', '01052', '01067', '01095', '01107', '01119', '01139', '01158', '01161', '01166', '01170', '01207', '01210', '01270', '01278', '01279', '01282', '01297', '01320', '01332', '01350', '01357', '01358', '01392', '01411', '01435', '01441', '01458', '01473', '01497', '01511', '01526', '01542', '01544', '01573', '01578', '01587', '01605', '01607', '01612', '01684', '01689', '01691', '01717', '01721', '01735', '01744', '01770', '01793', '01801', '01810', '01830', '01832', '01846', '01847', '01848', '01869', '01900', '01957', '01997', '02011', '02012', '02014', '02039', '02044', '02064', '02066', '02119', '02152', '02171', '02174', '02175', '02233', '02252', '02261', '02274', '02278', '02294', '02323', '02372', '02376', '02409', '02410', '02431', '02438', '02444', '02503', '02531', '02538', '02541', '02550', '02556', '02562', '02597', '02600', '02618', '02625', '02627', '02641', '02662', '02673', '02680', '02700', '02704', '02709', '02733', '02750', '02779', '02794', '02839', '02856', '02860', '02878', '02884', '02890', '02925', '02928', '02932', '02951', '02958', '02985', '02992', '02997', '03012', '03015', '03034', '03080', '03083', '03093', '03094', '03121', '03126', '03146', '03147', '03148', '03153', '03158', '03166', '03175', '03179', '03181', '03204', '03205', '03207', '03220', '03226', '03231', '03234', '03248', '03271', '03279', '03289', '03297', '03304', '03308', '03348', '03364', '03376', '03426', '03429', '03435', '03438', '03445', '03473', '03478', '03491', '03497', '03509', '03513', '03525', '03536', '03552', '03558', '03560', '03571', '03572', '03607', '03617', '03650', '03667', '03668', '03681', '03700', '03739', '03740', '03811', '03821', '03836', '03844', '03875', '03881', '03886', '03906', '03911', '03946', '03948', '03950', '03967', '03975', '03987', '03999', '04000', '04016', '04023', '04032', '04036', '04052', '04080', '04104', '04109', '04135', '04185', '04218', '04224', '04248', '04280', '04282', '04290', '04303', '04354', '04367', '04377', '04387', '04412', '04445', '04464', '04469', '04480', '04485', '04493', '04494', '04501', '04546', '04548', '04555', '04559', '04566', '04592', '04599', '04601', '04603', '04605', '04618', '04637', '04642', '04651', '04694', '04748', '04752', '04763', '04790', '04801', '04813', '04816', '04818', '04878', '04911', '04912', '04958', '04978', '04982', '04984', '04997', '05002', '05013', '05017', '05023', '05034', '05036', '05046', '05084', '05109', '05142', '05146', '05148', '05149', '05158', '05230', '05279', '05285', '05303', '05335', '05349', '05371', '05382', '05395', '05397', '05401', '05419', '05424', '05440', '05484', '05490', '05546', '05548', '05555', '05573', '05600', '05614', '05629', '05643', '05663', '05676', '05684', '05705', '05729', '05745', '05750', '05762', '05763', '05779', '05797', '05800', '05814', '05825', '05854', '05943', '06093', '06109', '06129', '06161', '06170', '06182', '06191', '06195', '06200', '06215', '06216', '06249', '06252', '06265', '06266', '06268', '06269', '06270', '06271', '06272', '06273', '06281', '06282', '06287', '06296', '06298', '06305', '06312', '06314', '06336', '06338', '06347', '07075', '07077', '07079', '07099', '07244', '07285', '07321', '07323', '07326', '07327', '07328', '07329', '07333', '07334', '07335', '07337', '07343', '07350', '07351', '07361', '07364', '07367', '07368', '07370', '07372', '07389', '07393', '07394', '07395', '07418', '07419', '07420', '07421', '07423', '07428', '07430', '07432', '07500', '13654', '13662', '13675', '13688', '13699', '13710', '13711', '13712', '13774', '13776', '13777', '14138', '14301', '15512', '15832', '15833', '15834', '15836', '15839', '15840', '15843', '15845', '19126', '19140', '19225', '19246', '19270', '19271', '19272', '19275', '19299', '19361', '19362']

gaugedata = {"id": [], "prec_mm": []}
gauge_files = [f for f in listdir("opendata.dwd.de/example_data/hourly_data/") if isfile(join("opendata.dwd.de/example_data/hourly_data/", f))]

# Go through data files and fill gauge dict with id and precipitation.
for file in gauge_files:
    date_start = datetime.datetime.strptime(file[18:26], '%Y%m%d')
    date_end = datetime.datetime.strptime(file[27:35], '%Y%m%d')
    date_of_interest = datetime.datetime(year=2019, month=1, day=9)
    if date_start < date_of_interest < date_end:
        gauge_id = file[36:41]
        with open("opendata.dwd.de/example_data/hourly_data/"+file) as f:
            for line in f:
                line_split = [x.strip() for x in line.split(';')]
                if "2019010912" in line_split[1]:
                    g_id = line_split[0].zfill(5)
                    if g_id in gauges_in_domain:
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
            line = ' '.join(line.split()) # reduce whitespaces
            f2.write(line+"\n") 
            line = [x.strip() for x in line.split(' ')] # split string
            gauge_id = line[0]
            for i in range(len(gaugedata["id"])): # Go through gauge dict.
                if gaugedata["id"][i] == gauge_id:
                    east, north = latlon_to_utm33N(line[5], line[4])
                    # gaugedata["easting"][i] = east
                    # gaugedata["northing"][i] = north
                    gaugedata["easting"][i] = min(xgrid, key=lambda x:abs(x-east)) # get closest pixel val in xgrid
                    gaugedata["northing"][i] = min(ygrid, key=lambda x:abs(x-north)) # get closest pixel val in ygrid
                    gaugedata["elevation"][i] = line[3]               

# print(gaugedata["id"][0], gaugedata["easting"][0], gaugedata["northing"][0])

# radar data: 1D-array, radar coords: 2D-array
radar_1d = radar.reshape([700*700]) # 1D-array (700*700) for radar data
radar_coords = util.gridaspoints(ygrid, xgrid) # 2D-array
gridshape = len(xgrid), len(ygrid)

# gauge data: 1D-array, gauge coords: 2D-array
obs = np.array(gaugedata["prec_mm"]) # 1D-array
obs_coords = zip(gaugedata["easting"], gaugedata["northing"]) # 2D-array
obs_coords = np.array([list(elem) for elem in obs_coords])
print("number of obs:", len(obs))

# Apply adjustment methods adn reshape 1D-array to 2D-array.
addadjuster = adjust.AdjustAdd(obs_coords, radar_coords)
addadjusted = addadjuster(obs, radar_1d)
addadjusted_arr = addadjusted.reshape(gridshape)

multadjuster = adjust.AdjustMultiply(obs_coords, radar_coords)
multadjusted = multadjuster(obs, radar_1d) 
multadjusted_arr = multadjusted.reshape(gridshape)

mfbadjuster = adjust.AdjustMFB(obs_coords, radar_coords)
mfbadjusted = mfbadjuster(obs, radar_1d)
mfbadjusted_arr = mfbadjusted.reshape(gridshape)

# Plot additive adjustment.
fig = pl.figure(figsize=(10, 8))
ax = pl.subplot(111, aspect="equal")
pl.xlim(min(xgrid), max(xgrid))
pl.ylim(min(ygrid), max(ygrid))
pm = ax.pcolormesh(xgrid, ygrid, addadjusted_arr, cmap=cm, vmin=0)
cbar = pl.colorbar(pm)
pl.title(f"Additive adjustment\nAdditive value between {np.round(np.nanmin(addadjusted_arr-radar),2)} and {np.round(np.nanmax(addadjusted_arr-radar),2)}")
pl.savefig("adjustment_add", dpi=600)

# Plot multiplicative adjustment.
fig = pl.figure(figsize=(10, 8))
ax = pl.subplot(111, aspect="equal")
pl.xlim(min(xgrid), max(xgrid))
pl.ylim(min(ygrid), max(ygrid))
pm = ax.pcolormesh(xgrid, ygrid, multadjusted_arr, cmap=cm, vmin=0)
cbar = pl.colorbar(pm)
pl.title(f"Multiplicative adjustment\nfactor between {np.round(np.nanmin(multadjusted_arr - radar),2)} and {np.round(np.nanmax(multadjusted_arr - radar),2)}")
pl.savefig("adjustment_mul", dpi=600)

# Plot difference in additive adjustment.
fig = pl.figure(figsize=(10, 8))
ax = pl.subplot(111, aspect="equal")
pl.xlim(min(xgrid), max(xgrid))
pl.ylim(min(ygrid), max(ygrid))
diff = addadjusted_arr - radar
pm = ax.pcolormesh(xgrid, ygrid, diff, cmap=cm)
cbar = pl.colorbar(pm)
pl.title("Additive adjustment difference")
pl.savefig("adjustment_add_diff", dpi=600)

# Plot difference in multiplicative adjustment.
fig = pl.figure(figsize=(10, 8))
ax = pl.subplot(111, aspect="equal")
pl.xlim(min(xgrid), max(xgrid))
pl.ylim(min(ygrid), max(ygrid))
diff = multadjusted_arr - radar
pm = ax.pcolormesh(xgrid, ygrid, diff, cmap=cm)
cbar = pl.colorbar(pm)
pl.title("Multiplicative adjustment difference")
pl.savefig("adjustment_mul_diff", dpi=600)