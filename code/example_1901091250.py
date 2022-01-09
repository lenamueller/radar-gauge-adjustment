# Radar postprocessing workflow example: 09.01.2019, Radar Dresden

import datetime
import numpy as np
import matplotlib.pylab as pl
import wradlib as wrl

import func
from colorbar import cm


# Configure filename and path.
filename = 'raa00-dx_10488-1901091250-drs---bin'
fpath = 'example_data/'

# Configure radar location and elevation.
radar_location = (13.769722, 51.125278, 263) # (lon, lat, alt) in decimal degree and meters.
elevation = 0.8 # elevation in degree.

# Read data.
f = wrl.util.get_wradlib_data_file(fpath+filename)
data, metadata = wrl.io.read_dx(f)

# Get date and time.
dt = datetime.datetime.strptime(filename[15:25], "%y%m%d%H%M")

# Plot reflectivity of raw data.
func.plot_rawdata(data, dt, filename)

# Clutter correction.
clmap, data_no_clutter = func.clutter_gabella(data, dt, filename)

# Attenuation correction.
att, data_attcorr = func.attenuation_corr(data_no_clutter, dt, filename)

# Apply ZR-relation (a=200, b=1.6) to get precipitation rates.
R = wrl.zr.z_to_r(wrl.trafo.idecibel(data_attcorr))

# Integrate rainfall rates to rainfall depth for 300sec.
depths = wrl.trafo.r_to_depth(R, 300)
func.plot_raindepths(depths, dt, filename)

# Create cartesian grid and reproject into UTM Zone 33 (EPSG-number 32633)
ranges = np.arange(0, 128000., 1000.) # in meters
azimuths = np.arange(0,360) # in degrees
polargrid = np.meshgrid(ranges, azimuths)
coords, rad = wrl.georef.polar.spherical_to_xyz(polargrid[0], polargrid[1], elevation, radar_location) # range, azimut, elevation, radar location, coords: (1,360,128,3)-array
utm = wrl.georef.epsg_to_osr(32633)
utm_coords = wrl.georef.reproject(coords, projection_source=rad, projection_target=utm)
x = utm_coords[..., 0]
y = utm_coords[..., 1]
z = utm_coords[..., 2]

# Create cartesian coordinates of the composite (UTM).
xgrid = np.linspace(x.min(), x.max(), 250) # first two arguments: area of interest, third argument: resolution
ygrid = np.linspace(y.min(), y.max(), 250)
grid_xy = np.meshgrid(xgrid, ygrid) # 2 lists of 100 lists
grid_xy = np.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose() # (1000,2) - array -> [lat, lon] for each cell

# Create cartesian coordinates of the radar bins.
xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)

# Interpolate data to composite grid.
gridded = wrl.comp.togrid(src=xy, trg=grid_xy, 
                          radius=128000., center=np.array([x.mean(), y.mean()]), 
                          data=depths.ravel(), interpol=wrl.ipol.Idw) # Nearest or Idw
gridded = np.ma.masked_invalid(gridded).reshape((len(xgrid), len(ygrid)))

# Plot gridded radar field.
fig = pl.figure(figsize=(10, 8))
ax = pl.subplot(111, aspect="equal")
pm = pl.pcolormesh(xgrid, ygrid, gridded, cmap=cm)
cbar = pl.colorbar(pm, shrink=0.75)
cbar.set_label("5 min - Rain depths (mm)", fontsize=15)
pl.xlabel("Easting (m)", fontsize=15)
pl.ylabel("Northing (m)", fontsize=15)
pl.title(f'Rain depths at {dt.strftime("%d-%m-%Y %H:%M")}\nDWD RADAR 10488 Dresden\nGridded to UTM Zone 33 (EPSG 32633)', fontsize=15)
pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_grid_1km2.png", dpi=600)


# Read gauge data.

# Apply RADAR-gauge adjustment methods.

# Evaluate RADAR-gauge adjustment methods.