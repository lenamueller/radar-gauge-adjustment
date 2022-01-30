import sys
import numpy as np
import shapefile as shp
import wradlib as wrl
import matplotlib.pylab as pl
import matplotlib.pyplot as plt
from pyproj import Proj

from colorbars import cm_latest
from func import max_from_arrays


# Retrieve arguments.
a = int(sys.argv[1])
b = float(sys.argv[2])

# Set projection.
myProj = Proj("+proj=utm +zone=32 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

# Metadata from https://www.dwd.de/DE/derdwd/messnetz/atmosphaerenbeobachtung/_functions/HaeufigGesucht/koordinaten-radarverbund.html
stations = {"abbr":["asb", "boo", "drs", "eis", "ess", "fbg","fld", "hnr", "isn", "mem", "neu", "nhb", "oft", "pro", "ros", "tur", "umd"], 
            "wmonr":[10103, 10132, 10488, 10780, 10410, 10908, 10440, 10339,10873,10950,10557,10605,10629,10392,10169,10832,10356], 
            "lat":[53.564011, 54.004381, 51.124639, 49.540667, 51.405649, 47.873611, 51.311197, 52.460083, 48.174705, 48.042145, 50.500114, 50.109656, 49.984745,  52.648667, 54.175660, 48.585379, 52.160096],
            "lon":[6.748292, 10.046899, 13.768639, 12.402788, 6.967111, 8.003611, 8.801998, 9.694533, 12.101779, 10.219222, 11.135034, 6.548328, 8.712933, 13.858212, 12.058076, 9.78267, 11.176091],
            "elev":[36, 125, 263, 799, 185, 1516, 628, 98, 678, 724, 880, 586, 246, 194, 37, 768, 185]}

# Create polar grid.
elevation = 0.5 # degree
azimuths = np.arange(0,360) # degrees
ranges = np.arange(0, 128000., 1000.) # meters
polargrid = np.meshgrid(ranges, azimuths)

# Create xy grid.
xgrid = np.linspace(100000, 1000000, 1000)
ygrid = np.linspace(5200000, 6200000, 1000)
grid_xy = np.meshgrid(xgrid, ygrid)
grid_xy = np.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose()

# Read datetime from metadata.
f = wrl.util.get_wradlib_data_file(f"weather/radar/sites/dx/drs/raa00-dx_10488-latest-drs---bin")
data, metadata = wrl.io.read_dx(f)
dt = metadata["datetime"]
dt_str = dt.strftime("%A, %Y-%m-%d %H:%M")

# Read relfectivity and calculate rain depths.
def get_gridded_depths(abbr, wmonr):
    """Read data and apply clutter and attenuation correction."""
    index = stations['abbr'].index(abbr)
    site_loc = (stations['lon'][index], stations['lat'][index], stations['elev'][index])
    f = wrl.util.get_wradlib_data_file(f"weather/radar/sites/dx/{abbr}/raa00-dx_{wmonr}-latest-{abbr}---bin")
    data, metadata = wrl.io.read_dx(f)
    clmap = wrl.clutter.filter_gabella(data, wsize=5, thrsnorain=0., tr1=6., n_p=8, tr2=1.3)
    data_no_clutter = wrl.ipol.interpolate_polar(data, clmap)
    att = wrl.atten.correct_attenuation_constrained(data_no_clutter, a_max=1.67e-4, a_min=2.33e-5, n_a=100, b_max=0.7, b_min=0.65, n_b=6,
                                                    gate_length=1., constraints=[wrl.atten.constraint_dbz, wrl.atten.constraint_pia], 
                                                    constraint_args=[[59.0],[20.0]])
    data_attcorr = data_no_clutter + att
    R = wrl.zr.z_to_r(wrl.trafo.idecibel(data_attcorr), a=200, b=1.6)
    depths = wrl.trafo.r_to_depth(R, 300)
    coords, rad = wrl.georef.spherical_to_xyz(polargrid[0], polargrid[1], elevation, site_loc)
    utm_coords = wrl.georef.reproject(coords, projection_source=rad,projection_target = wrl.georef.epsg_to_osr(32632))
    x = utm_coords[..., 0]
    y = utm_coords[..., 1]
    xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)
    gridded = wrl.comp.togrid(xy, grid_xy, 128000., np.array([x.mean(), y.mean()]), depths.ravel(), wrl.ipol.Nearest)
    gridded = gridded.reshape((len(xgrid), len(ygrid)))
    return gridded

depths_list = [get_gridded_depths(a, b) for a,b in zip(stations['abbr'], stations["wmonr"])]

# Merge radar domains.      
radar = np.empty((1000, 1000))
radar[:] = np.NaN
for i in range(len(depths_list)):    
    radar = max_from_arrays(radar, depths_list[i])

# Replace negative numbers with zero.
radar[radar<0] = 0

# Plot composite.
pl.figure(figsize=(10, 8))
ax = pl.subplot(111, aspect="equal")
pm = ax.pcolormesh(xgrid, ygrid, radar, cmap=cm_latest, vmin=0.0, vmax=0.8)
cbar = pl.colorbar(pm, ticks=[0,0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8])
cbar.ax.set_yticklabels(["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8 <"])
cbar.ax.tick_params(labelsize=14) 
cbar.set_label(f"5 min - rain depths (mm)", fontsize=14)
# Add country shp.
sf = shp.Reader("geodata/DEU_adm1_multiline.shp")
lines_seperated = []
for shape in sf.shapes():
    all_parts = shape.parts
    all_parts.append(len(shape.points[:]))
    for i in range(len(shape.parts)-1):
        line_begin = all_parts[i]
        line_end = all_parts[i+1]-1
        lines_seperated.append(shape.points[line_begin:line_end])
        x = [i[0] for i in shape.points[line_begin:line_end]]
        y = [i[1] for i in shape.points[line_begin:line_end]]
        # reproject into UTM
        east, north = [], []
        for j in range(len(x)):
            e, n = myProj(x[j], y[j])
            east.append(e)
            north.append(n)
        plt.plot(east, north, lw=0.5, c="k")
pl.xlabel("Easting (m)", fontsize=14)
pl.ylabel("Northing (m)", fontsize=14)
ax.ticklabel_format(useOffset=False, style='plain')
ax.tick_params(axis='both', which='major', labelsize=14)
pl.xlim(200000, max(xgrid))
pl.ylim(5200000, 6150000)
pl.xticks(ticks=np.arange(200000,1200000,200000))
pl.yticks(ticks=np.arange(5200000,6200000,200000))
pl.grid(lw=0.5, zorder=10)
pl.title(f"Precipitation Radar\n{dt_str} UTC", fontsize=14)
x = dt.strftime("%Y-%m-%d-%H%M")
pl.savefig(f"images/latest/RAD_composite_{x}", dpi=600)