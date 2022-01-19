import numpy as np
import wradlib as wrl
import matplotlib.pylab as pl

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

domain = blending_radar_domains(np.zeros((700,700)), gridded_drs)
domain = blending_radar_domains(domain, gridded_eis)
domain = blending_radar_domains(domain, gridded_pro)
domain = blending_radar_domains(domain, gridded_umd)
domain = blending_radar_domains(domain, gridded_neu)

# Save grid information to files.
np.savetxt("geodata/xgrid.txt", xgrid, fmt = "%.4f")
np.savetxt("geodata/ygrid.txt", ygrid, fmt = "%.4f")
np.savetxt("geodata/griddata.txt", domain, fmt = "%.4f")

fig = pl.figure(figsize=(10,8))
ax = pl.subplot(111, aspect="equal") # aspect=111/71
pm = pl.pcolormesh(xgrid, ygrid, domain, cmap=cm, vmax=0.3, label="x")
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
pl.savefig(f"images/composite_{filename_drs[15:25]}_utm", dpi=600)