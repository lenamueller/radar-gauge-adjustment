import sys
import wradlib as wrl

from func import plot_polar, cm_clutter
from func import clutter_gabella, attcorr, plot_attenuation_mean_bin, plot_attenuation_per_bin, rain_depths, plot_raindepths


# Retrieve arguments from shell script.
filename = sys.argv[1]
minutes = int(sys.argv[2])
print(filename, " - Clutter and attenuation correction. Calculate rain depths.")

# Read and plot raw data.
f = wrl.util.get_wradlib_data_file('example_data/'+filename)
data, metadata = wrl.io.read_dx(f)
plot_polar(data, filename, "Raw data", "raw")

# Clutter correction
clmap, data_no_clutter = clutter_gabella(data, filename)
plot_polar(data=clmap, filename=filename, what="cluttermap", subtitle="Detected clutter", cm=cm_clutter, plot_cbar=False)
plot_polar(data=data_no_clutter, filename=filename, what="noclutter", subtitle="After clutter correction")    

# Attenuation correction
att, data_attcorr = attcorr(data_no_clutter, filename)
plot_polar(data=att, filename=filename, subtitle="Attenuation error", what="att", cm="Reds", cbarlabel="$\Delta$ Reflectivity (dBZ)")
plot_polar(data=data_attcorr, filename=filename, subtitle="After attenuation correction", what="attcorr")
plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, 0)
plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, 90)
plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, 180)
plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, 270)
plot_attenuation_mean_bin(data_no_clutter, data_attcorr, filename)

# Get rain depths.
depths = rain_depths(data_attcorr, filename, minutes)
plot_raindepths(depths, filename, minutes)