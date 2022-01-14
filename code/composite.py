import sys
import datetime
import numpy as np
import matplotlib.pylab as pl
import matplotlib.pyplot as plt
import wradlib as wrl
from wradlib.georef.projection import reproject
import cartopy.crs as ccrs

from colorbar import cm
from func import plot_raindepths, plot_gridded, clutter_gabella, attcorr,  rain_depths


filename_drs = "raa00-dx_10488-1901091200-drs---bin"
filename_pro = "raa00-dx_10392-1901091200-pro---bin"
filename_umd = "raa00-dx_10356-1901091200-umd---bin"
filename_neu = "raa00-dx_10557-1901091200-neu---bin"
filename_eis = "raa00-dx_10780-1901091200-eis---bin"

site_loc_drs = (13.769722, 51.125278, 263)
site_loc_pro = (13.858212, 52.648667, 194)
site_loc_umd = (11.176091, 52.160096, 185)
site_loc_neu = (11.135034, 50.500114, 880)
site_loc_eis = (12.402788, 49.540667, 799)

# get domain width and heigth, 135km 
lon_min = 11.135034
lon_max = 13.858212
lat_min = 49.540667
lat_max = 52.648667

# Calculate rain depths as (360,128) - array.
def get_depths(filename):
    """ 
    Read data from file. Correct clutter and attenuation. Calculate and return 5min - rain depths.
    """
    f = wrl.util.get_wradlib_data_file('example_data/'+filename)
    data, metadata = wrl.io.read_dx(f)
    clmap, data_no_clutter = clutter_gabella(data, filename)
    att, data_attcorr = attcorr(data_no_clutter, filename)
    depths = rain_depths(data_attcorr, filename, 300)    
    return depths

# Calculate rain depths in polar coordinates.
depths_drs = get_depths(filename_drs)
depths_pro = get_depths(filename_pro)
depths_umd = get_depths(filename_umd)
depths_neu = get_depths(filename_neu)
depths_eis = get_depths(filename_eis)
np.savetxt("code/depths_drs.txt", depths_drs)

# Gridding
def get_radolan_coords(depths, radar_loc):
    # Get cartesian coordinates in xyz-space.
    elevation = 0.5 # in degree
    azimuths = np.arange(0,360)
    ranges = np.arange(0, 128000., 1000.)
    polargrid = np.meshgrid(ranges, azimuths)
    coords, rad = wrl.georef.spherical_to_xyz(polargrid[0], polargrid[1], elevation, radar_loc)

    # Get geo coordinates.
    utm_coords = wrl.georef.reproject(coords, projection_source=rad, projection_target=wrl.georef.epsg_to_osr(32632))
    x = utm_coords[..., 0]
    y = utm_coords[..., 1]
    # radolan = wrl.georef.create_osr("dwd-radolan") # polarstereografischer Projektion, äquidistante Rasterung von 1,0 km
    # radolan_coords = wrl.georef.reproject(coords, projection_source=rad, projection_target=radolan)
    # x = radolan_coords[..., 0]
    # y = radolan_coords[..., 1]

    # Gridding -> 2D array
    xgrid = np.linspace(x.min(), x.max(), 250)
    ygrid = np.linspace(y.min(), y.max(), 250)
    grid_xy = np.meshgrid(xgrid, ygrid)
    grid_xy = np.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose()
    xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)
    gridded = wrl.comp.togrid(xy, grid_xy, 128000., np.array([x.mean(), y.mean()]), depths.ravel(), wrl.ipol.Idw)
    gridded = np.ma.masked_invalid(gridded).reshape((len(xgrid), len(ygrid)))
    return xgrid, ygrid, gridded

xgrid_drs, ygrid_drs, gridded_drs = get_radolan_coords(depths_drs, site_loc_drs)
xgrid_eis, ygrid_eis, gridded_eis = get_radolan_coords(depths_eis, site_loc_eis)
xgrid_pro, ygrid_pro, gridded_pro = get_radolan_coords(depths_pro, site_loc_pro)
xgrid_umd, ygrid_umd, gridded_umd = get_radolan_coords(depths_umd, site_loc_umd)
xgrid_neu, ygrid_neu, gridded_neu = get_radolan_coords(depths_neu, site_loc_neu)
np.savetxt("code/gridded_drs.txt", gridded_drs)

# Plotting
fig = pl.figure(figsize=(10,8))
ax = pl.subplot(111, aspect="equal")
# ax = pl.axes(projection=ccrs.PlateCarree())
# ax.coastlines()
# ax.gridlines(draw_labels=True)
pm1 = pl.pcolormesh(xgrid_drs, ygrid_drs, gridded_drs, cmap=cm)
pm2 = pl.pcolormesh(xgrid_eis, ygrid_eis, gridded_eis, cmap=cm)
pm3 = pl.pcolormesh(xgrid_pro, ygrid_pro, gridded_pro, cmap=cm)
pm4 = pl.pcolormesh(xgrid_umd, ygrid_umd, gridded_umd, cmap=cm)
pm4 = pl.pcolormesh(xgrid_neu, ygrid_neu, gridded_neu, cmap=cm)
pl.colorbar()
pl.xlabel("Easting (m)")
pl.ylabel("Northing (m)")
pl.title("UTM Zone 33")
pl.savefig(f"images/composite_{filename_drs[15:25]}", dpi=600)