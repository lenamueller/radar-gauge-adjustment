import datetime
import numpy as np
import matplotlib.pylab as pl
import wradlib as wrl
import wradlib.clutter as clutter
import wradlib.util as util

import func

filename = 'raa00-dx_10488-1901091250-drs---bin'
fpath = 'example_data/'
radar_location = (13.769722, 51.125278, 263) # (lon, lat, alt) in decimal degree and meters
elevation = 0.8 # in degree

# Read data.
f = wrl.util.get_wradlib_data_file(fpath+filename)
data, metadata = wrl.io.read_dx(f)
print("data shape:", data.shape, "\nmetadata:", metadata.keys())
      
# Get date and time.
dt = datetime.datetime.strptime(filename[15:25], "%y%m%d%H%M")

# Plot reflectivity of raw data.
func.raw_plot(data, dt, filename)

# Clutter correction.
clmap, data_no_clutter = func.clutter_gabella(data, dt, filename)

# Attenuation correction.
att, data_attcorr = func.attenuation_corr(data_no_clutter, dt, filename)

# Apply ZR-relation (a=200, b=1.6) to get precipitation rates.
R = wrl.zr.z_to_r(wrl.trafo.idecibel(data_attcorr))

# Integrate rainfall rates to rainfall depth for 300sec.
depths = wrl.trafo.r_to_depth(R, 300)
func.rain_depths(depths, dt, filename)


# Further rainfall accumulation to hourly data.
# TODO

# Project polar in cartesian coordinates.
polargrid = np.meshgrid(np.arange(0, 128000., 1000.), np.arange(0,360)) # ranges in meters, azimuths in degrees
coords, rad = wrl.georef.spherical_to_xyz(polargrid[0], polargrid[1], elevation, radar_location)
x = coords[..., 0]
y = coords[..., 1]
utm = wrl.georef.epsg_to_osr(32633) # EPSG-number, UTM Zone 33
utm_coords = wrl.georef.reproject(coords, projection_source=rad, projection_target=utm)
radolan = wrl.georef.create_osr("dwd-radolan")
radolan_coords = wrl.georef.reproject(coords, projection_target=radolan)
xgrid = np.linspace(x.min(), x.max(), 200)
ygrid = np.linspace(y.min(), y.max(), 200)
grid_xy = np.meshgrid(xgrid, ygrid)
grid_xy = np.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose()
xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)
gridded = wrl.comp.togrid(xy, grid_xy, 128000., np.array([x.mean(), y.mean()]), data.ravel(), wrl.ipol.Nearest)
gridded = np.ma.masked_invalid(gridded).reshape((len(xgrid), len(ygrid)))

fig = pl.figure(figsize=(10,8))
ax = pl.subplot(111, aspect="equal")
pm = pl.pcolormesh(xgrid, ygrid, gridded)
cbar = pl.colorbar(pm, shrink=0.75)
cbar.set_label("Reflectivity (dBZ)")
pl.xlabel("Easting (m)")
pl.ylabel("Northing (m)")
pl.xlim(min(xgrid), max(xgrid))
pl.ylim(min(ygrid), max(ygrid))
pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} - DWD RADAR 10488 Dresden - Gridded', fontsize=11)
pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_grid.png")
# Apply RADAR-gauge adjustment methods.