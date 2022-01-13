import sys
import numpy as np
import wradlib as wrl

from func import plot_radar, plot_raindepths, plot_gridded, clutter_gabella, attcorr, plot_attenuation_mean_bin, plot_attenuation_per_bin, rain_depths


# Configure filename, path, radar elevation and location
filename = sys.argv[1]
print(filename)
radar_location = (float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])) # lat, lon, height
elevation = 0.8

# Read data.
f = wrl.util.get_wradlib_data_file('example_data/' + filename)
data, md = wrl.io.read_dx(f)

# Plot raw data.
plot_radar(data, filename, what="raw", subtitle="Raw data")

# Clutter correction.
clmap, data_no_clutter = clutter_gabella(data, filename)

# Attenuation correction.
att, data_attcorr = attcorr(data_no_clutter, filename)
plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, bin=0)
plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, bin=90)
plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, bin=180)
plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, bin=270)
plot_attenuation_mean_bin(data_no_clutter, data_attcorr, filename)

# Calculate rain depths from reflectivity.
depths = rain_depths(data=data_attcorr, filename=filename, duration_sec=300)

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

# Save UTM grid coordinates in txt-file.
np.savetxt("code/grid_xy.txt", grid_xy, fmt = "%.4f,%.4f")
    
# Create cartesian coordinates of the radar bins.
xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)

# Interpolate data to composite grid.
gridded = wrl.comp.togrid(src=xy, trg=grid_xy, 
                          radius=128000., center=np.array([x.mean(), y.mean()]), 
                          data=depths.ravel(), interpol=wrl.ipol.Idw) # Nearest or Idw
gridded = np.ma.masked_invalid(gridded).reshape((len(xgrid), len(ygrid)))

# Plot gridded radar field.
plot_gridded(xgrid, ygrid, gridded, filename, subtitle="Gridded to UTM Zone 33 (EPSG 32633)")


# Read gauge metadata.
# gauges_metadata = []
# file_data = open('geodata/RR_stations_150km_UTM.csv')
# for row in file_data:
#     gauges_metadata.append(row.split(";"))
    
# gauges_metadata = np.array(gauges_metadata)

# Create index list for gauges.
 
# Apply RADAR-gauge adjustment methods.

# Evaluate RADAR-gauge adjustment methods.