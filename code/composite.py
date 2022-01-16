from re import A
import sys
import datetime
import numpy as np
import matplotlib.pylab as pl
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


# Gridding into EPSG 4326 (default)
def get_coords(depths, radar_loc, centerxy):
    # Get cartesian coordinates in xyz-space.
    elevation = 0.5 # in degree
    azimuths = np.arange(0,360)
    ranges = np.arange(0, 128000., 1000.)
    polargrid = np.meshgrid(ranges, azimuths)
    coords, rad = wrl.georef.spherical_to_xyz(polargrid[0], polargrid[1], elevation, radar_loc)
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
                              center = centerxy,
                              data=depths.ravel(), interpol=wrl.ipol.Idw)

    # gridded = np.ma.masked_invalid(gridded).reshape((len(xgrid), len(ygrid)))
    gridded = gridded.reshape((len(xgrid), len(ygrid)))
    return xgrid, ygrid, gridded, rad

xgrid_drs, ygrid_drs, gridded_drs, rad = get_coords(depths_drs, site_loc_drs, np.array([0,0]))
xgrid_eis, ygrid_eis, gridded_eis, rad = get_coords(depths_eis, site_loc_eis, np.array([-95000,-176000]))
xgrid_pro, ygrid_pro, gridded_pro, rad = get_coords(depths_pro, site_loc_pro, np.array([6000,169000]))
xgrid_umd, ygrid_umd, gridded_umd, rad = get_coords(depths_umd, site_loc_umd, np.array([-181000,69000]))
xgrid_neu, ygrid_neu, gridded_neu, rad = get_coords(depths_neu, site_loc_neu, np.array([-184000,-69000]))

# Blending domains. Take maximum value of two cutting domains.
def blending_radar_domains(domain, gridded_data):
    # Change nan's to zeros. Choose element wise maximum.
    return np.maximum(domain, np.nan_to_num(gridded_data))

d2 = blending_radar_domains(np.zeros((700, 700)), gridded_drs)
d3 = blending_radar_domains(d2, gridded_eis)
d4 = blending_radar_domains(d3, gridded_pro)
d5 = blending_radar_domains(d4, gridded_umd)
domain_final = blending_radar_domains(d5, gridded_neu)

# Georeferencing
xgrid, ygrid = wrl.georef.reproject(xgrid_drs, ygrid_drs, projection_source=rad, 
                                            projection_target = wrl.georef.epsg_to_osr(25832)) # UTM Zone 33N: 25832, WGS: 4326

np.savetxt("code/xgrid.txt", xgrid, fmt = "%.4f")
np.savetxt("code/ygrid.txt", ygrid, fmt = "%.4f")
np.savetxt("code/domain_final.txt", domain_final, fmt = "%.4f")
np.savetxt("code/utmgrid.txt", np.column_stack((xgrid, ygrid)), fmt = "%.4f")

# Plotting
fig = pl.figure(figsize=(10,8))
ax = pl.subplot(111, aspect="equal")
pl.pcolormesh(xgrid, ygrid, domain_final, cmap=cm, vmax=0.3)
cbar = pl.colorbar()
cbar.ax.tick_params(labelsize=15) 
cbar.set_label("5 min - rain depths (mm)", fontsize=15)
pl.grid(lw=0.5)
pl.xlabel("easting", fontsize=15)
pl.ylabel("northing", fontsize=15)
pl.savefig(f"images/composite_{filename_drs[15:25]}_utm", dpi=600)