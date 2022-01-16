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
    Read data from file. Correct clutter and attenuation. Calculate and return 5min - rain depths as (360   ,128) - array.
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

# georeferencing
wgs = wrl.georef.epsg_to_osr(4326) # default
utm = wrl.georef.epsg_to_osr(25833) # UTM Zone 33N

# Gridding into EPSG 4326 (default)
def get_coords(depths, radar_loc, centerxy):
    # Get cartesian coordinates in xyz-space.
    elevation = 0.5 # in degree
    azimuths = np.arange(0,360)
    ranges = np.arange(0, 128000., 1000.)
    polargrid = np.meshgrid(ranges, azimuths)
    coords, rad = wrl.georef.spherical_to_xyz(polargrid[0], polargrid[1], elevation, radar_loc)
    # coords = wrl.georef.projection.spherical_to_proj(polargrid[0], polargrid[1], projection_target=utm)
    
    
    x = coords[..., 0]
    y = coords[..., 1]
    x = x + centerxy[0]
    y = y + centerxy[1]
    
    # Gridding -> 2D array
    xgrid = np.linspace(-350000,350000,700)
    ygrid = np.linspace(-350000,350000,700)
    grid_xy = np.meshgrid(xgrid, ygrid)
    grid_xy = np.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose()
    xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)
    gridded = wrl.comp.togrid(src=xy, trg=grid_xy, 
                              radius=128000., 
                            #   center=np.array([0,0]),
                              center = centerxy,
                              data=depths.ravel(), 
                              interpol=wrl.ipol.Idw)

    # gridded = np.ma.masked_invalid(gridded).reshape((len(xgrid), len(ygrid)))
    gridded = gridded.reshape((len(xgrid), len(ygrid)))
    return xgrid, ygrid, gridded, rad

xgrid_drs, ygrid_drs, gridded_drs, rad = get_coords(depths_drs, site_loc_drs, np.array([0,0]))
xgrid_eis, ygrid_eis, gridded_eis, rad = get_coords(depths_eis, site_loc_eis, np.array([-95000,-176000]))
xgrid_pro, ygrid_pro, gridded_pro, rad = get_coords(depths_pro, site_loc_pro, np.array([6000,169000]))
xgrid_umd, ygrid_umd, gridded_umd, rad = get_coords(depths_umd, site_loc_umd, np.array([-181000,69000]))
xgrid_neu, ygrid_neu, gridded_neu, rad = get_coords(depths_neu, site_loc_neu, np.array([-184000,-69000]))


def radar_into_domain(domain, gridded_data):
    """ 
    Change nan's to zeros. Choose element wise maximum and insert in main domain.
    """
    return np.maximum(domain, np.nan_to_num(gridded_data))

d2 = radar_into_domain(np.zeros((700,700)), gridded_drs)
d3 = radar_into_domain(d2, gridded_eis)
d4 = radar_into_domain(d3, gridded_pro)
d5 = radar_into_domain(d4, gridded_umd)
domain_final = radar_into_domain(d5, gridded_neu)



# Plotting
fig = pl.figure(figsize=(10,8))
ax = pl.subplot(111, aspect="equal")
pl.pcolormesh(xgrid_drs, ygrid_drs, domain_final, cmap=cm)
cbar = pl.colorbar()
cbar.ax.tick_params(labelsize=15) 
cbar.set_label("5 min - rain depths (mm)", fontsize=15)
pl.grid(lw=0.5)
# pl.xlabel("distance (km)")
# pl.ylabel("distance (km)")
pl.title("Centered at RADAR site Dresden (WMO no. 10488)", fontsize=12)
pl.savefig(f"images/composite_{filename_drs[15:25]}_new", dpi=600)