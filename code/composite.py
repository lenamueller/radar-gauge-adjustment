import sys
import datetime
import numpy as np
import wradlib as wrl
from wradlib.georef.projection import reproject

from func import plot_raindepths, plot_gridded, clutter_gabella, attcorr,  rain_depths
from colorbar import cm

filename_drs='raa00-dx_10488-1901091200-drs---bin' # Dresden
filename_pro='raa00-dx_10392-1901091200-pro---bin' # Proetzel
filename_umd='raa00-dx_10356-1901091200-umd---bin' # Ummendorf
filename_neu='raa00-dx_10557-1901091200-neu---bin' # Neuhaus
filename_eis='raa00-dx_10780-1901091200-eis---bin' # Eisberg

# Calculate rain depths as (360,128) - array.
def get_depths(filename):
    f = wrl.util.get_wradlib_data_file('example_data/'+filename)
    data, metadata = wrl.io.read_dx(f)
    clmap, data_no_clutter = clutter_gabella(data, filename)
    att, data_attcorr = attcorr(data_no_clutter, filename)
    depths = rain_depths(data_attcorr, filename, 300)    
    return depths

depths_drs = get_depths(filename_drs)
depths_pro = get_depths(filename_pro)
depths_umd = get_depths(filename_umd)
depths_neu = get_depths(filename_neu)
depths_eis = get_depths(filename_eis)

# Create cartesian composite.
print(depths_drs.shape, type(depths_drs))
