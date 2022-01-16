from re import A
import sys
import datetime
import numpy as np
import matplotlib.pylab as pl
import matplotlib.pyplot as plt
import wradlib as wrl
from wradlib.georef.projection import reproject

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

def get_depths(filename):
    """ 
    Read data from file. Correct clutter and attenuation. Calculate and return 5min - rain depths as (360,128) - array.
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

# Gridding into EPSG 4326 (default)
def get_coords(depths, radar_loc):
    # Get cartesian coordinates in xyz-space.
    elevation = 0.5 # in degree
    azimuths = np.arange(0,360)
    ranges = np.arange(0, 128000., 1000.)
    polargrid = np.meshgrid(ranges, azimuths)
    coords, rad = wrl.georef.spherical_to_xyz(polargrid[0], polargrid[1], elevation, radar_loc)
    x = coords[..., 0]
    y = coords[..., 1]

    # Gridding -> 2D array
    xgrid = np.linspace(x.min(), x.max(), 256)
    ygrid = np.linspace(y.min(), y.max(), 256)
    grid_xy = np.meshgrid(xgrid, ygrid)
    grid_xy = np.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose()
    xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)
    gridded = wrl.comp.togrid(xy, grid_xy, 128000., np.array([0,0]), depths.ravel(), wrl.ipol.Idw)
    # gridded = np.ma.masked_invalid(gridded).reshape((len(xgrid), len(ygrid)))
    gridded = gridded.reshape((len(xgrid), len(ygrid)))
    return xgrid, ygrid, gridded, rad

xgrid_drs, ygrid_drs, gridded_drs, rad = get_coords(depths_drs, site_loc_drs)
xgrid_eis, ygrid_eis, gridded_eis, rad = get_coords(depths_eis, site_loc_eis)
xgrid_pro, ygrid_pro, gridded_pro, rad = get_coords(depths_pro, site_loc_pro)
xgrid_umd, ygrid_umd, gridded_umd, rad = get_coords(depths_umd, site_loc_umd)
xgrid_neu, ygrid_neu, gridded_neu, rad = get_coords(depths_neu, site_loc_neu)


# Calculate offset of sites pro, umd, eis, neu from site drs.
xgrid_pro = [x+6*1000 for x in xgrid_drs]
ygrid_pro = [y+169*1000 for y in ygrid_drs]
xgrid_eis = [x-95*1000 for x in xgrid_drs]
ygrid_eis = [y-176*1000 for y in ygrid_drs]
xgrid_neu = [x-184*1000 for x in xgrid_drs]
ygrid_neu = [y-69*1000 for y in ygrid_drs]
xgrid_umd = [x-181*1000 for x in xgrid_drs]
ygrid_umd = [y+69*1000 for y in ygrid_drs]
np.savetxt("code/xgrid_pro.txt", xgrid_pro, fmt = "%.4f")
np.savetxt("code/xgrid_drs.txt", xgrid_drs, fmt = "%.4f")

# Add data to domain
domain = np.zeros((700,550))
def radar_into_domain(gridded_data, x_offset, y_offset):
    """ 
    Change nan's to zeros. Choose element wise maximum and insert in main domain.
    """
    x_offset-= 128
    y_offset-= 128
    domain_new = np.maximum(domain[y_offset:y_offset+gridded_data.shape[0], x_offset:x_offset+gridded_data.shape[1]], np.nan_to_num(gridded_data))
    domain[y_offset:y_offset+gridded_data.shape[0], x_offset:x_offset+gridded_data.shape[1]] = domain_new
    

radar_into_domain(gridded_drs, 350, 350)
radar_into_domain(gridded_eis, 255, 174)
radar_into_domain(gridded_pro, 356, 519)
radar_into_domain(gridded_umd, 168, 419)
radar_into_domain(gridded_neu, 166 ,281)

# Plotting
fig = pl.figure(figsize=(10,8))
ax = pl.subplot(111, aspect="equal")
plt.imshow(domain, cmap=cm) # heatmap
cbar = pl.colorbar()
cbar.ax.tick_params(labelsize=15) 
cbar.set_label("5 min - rain depths (mm)", fontsize=15)
pl.xlim([0, 550])
pl.ylim([0, 700])
pl.xticks(ticks=np.arange(0,600,50), labels=np.arange(-350,250,50))
pl.yticks(ticks=np.arange(0,750,50), labels=np.arange(-350,400,50))
pl.grid(lw=0.5)
pl.xlabel("distance (km)")
pl.ylabel("distance (km)")
pl.title("Centered at RADAR site Dresden (WMO no. 10488)", fontsize=12)
pl.savefig(f"images/composite_{filename_drs[15:25]}_4326", dpi=600)