from audioop import add
import sys
import numpy as np
import wradlib as wrl
import matplotlib.pylab as pl
import wradlib.adjust as adjust
import wradlib.verify as verify
import wradlib.util as util

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

# gauge adjustment

# radar data: 1D-array, radar coords: 2D-array
radar_1d = radar.reshape([700*700]) # 1D-array (700*700) for radar data
radar_coords = util.gridaspoints(ygrid, xgrid) # 2D-array
gridshape = len(xgrid), len(ygrid)

# gauge data: 1D-array, gauge coords: 2D-array
obs = np.array([0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03]) # 1D-array
obs_coords = np.array([[299499.2847, 5699499.2847],[301502.1459, 5614377.6824],[299499.2847, 5699499.2847],
                       [299499.2847, 5699499.2847],[299499.2847, 5699499.2847],[299499.2847, 5699499.2847],
                       [299499.2847, 5699499.2847],[299499.2847, 5699499.2847],[299499.2847, 5699499.2847],
                       [299499.2847, 5699499.2847]]) # 2D-array

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
pm = ax.pcolormesh(xgrid, ygrid, addadjusted_arr, cmap=cm, vmin=0, vmax=0.4)
cbar = pl.colorbar(pm)
pl.title(f"Additive adjustment\nAdditive value: {np.round(np.nanmean(addadjusted_arr-radar),2)}")
pl.savefig("adjustment_add", dpi=600)

# Plot multiplicative adjustment.
fig = pl.figure(figsize=(10, 8))
ax = pl.subplot(111, aspect="equal")
pl.xlim(min(xgrid), max(xgrid))
pl.ylim(min(ygrid), max(ygrid))
pm = ax.pcolormesh(xgrid, ygrid, multadjusted_arr, cmap=cm, vmin=0, vmax=0.4)
cbar = pl.colorbar(pm)
pl.title(f"Multiplicative adjustment\nFaktor between {np.round(np.nanmin(multadjusted_arr - radar),2)} and {np.round(np.nanmax(multadjusted_arr - radar),2)}")
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