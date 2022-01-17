import imp
import sys
from turtle import right
import numpy as np
import wradlib as wrl
import matplotlib.pylab as pl

from colorbar import cm
from func import metadata, plot_radar, plot_raindepths, plot_gridded, clutter_gabella, attcorr, plot_attenuation_mean_bin, plot_attenuation_per_bin, rain_depths, get_coords, get_depths, blending_radar_domains, blending_radar_domains


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

# site_abb, site_text, dt = metadata(filename_drs)

# Calculate and plot rain depths in polar coordinates.
depths_drs = get_depths(filename_drs)
depths_pro = get_depths(filename_pro)
depths_umd = get_depths(filename_umd)
depths_neu = get_depths(filename_neu)
depths_eis = get_depths(filename_eis)

# Project radar domains into global xyz domain.
xgrid_drs, ygrid_drs, gridded_drs, rad = get_coords(depths_drs, site_loc_drs, np.array([0,0]))
xgrid_eis, ygrid_eis, gridded_eis, rad = get_coords(depths_eis, site_loc_eis, np.array([-95000,-176000]))
xgrid_pro, ygrid_pro, gridded_pro, rad = get_coords(depths_pro, site_loc_pro, np.array([6000,169000]))
xgrid_umd, ygrid_umd, gridded_umd, rad = get_coords(depths_umd, site_loc_umd, np.array([-181000,69000]))
xgrid_neu, ygrid_neu, gridded_neu, rad = get_coords(depths_neu, site_loc_neu, np.array([-184000,-69000]))

# Plot single radar fields in UTM Zone 33N.
plot_gridded(xgrid_drs, ygrid_drs, gridded_drs, filename_drs, "UTM Zone 33N (EPSG 25832)", proj_src=rad, proj_trg_epsgno=25832)
plot_gridded(xgrid_eis, ygrid_eis, gridded_eis, filename_eis, "UTM Zone 33N (EPSG 25832)", proj_src=rad, proj_trg_epsgno=25832)
plot_gridded(xgrid_pro, ygrid_pro, gridded_pro, filename_pro, "UTM Zone 33N (EPSG 25832)", proj_src=rad, proj_trg_epsgno=25832)
plot_gridded(xgrid_umd, ygrid_umd, gridded_umd, filename_umd, "UTM Zone 33N (EPSG 25832)", proj_src=rad, proj_trg_epsgno=25832)
plot_gridded(xgrid_neu, ygrid_neu, gridded_neu, filename_neu, "UTM Zone 33N (EPSG 25832)", proj_src=rad, proj_trg_epsgno=25832)


# Blending domains. Take maximum value of two cutting domains.
d2 = blending_radar_domains(np.zeros((700, 700)), gridded_drs)
d3 = blending_radar_domains(d2, gridded_eis)
d4 = blending_radar_domains(d3, gridded_pro)
d5 = blending_radar_domains(d4, gridded_umd)
domain_final = blending_radar_domains(d5, gridded_neu)

# Georeferencing
xgrid, ygrid = wrl.georef.reproject(xgrid_drs, ygrid_drs, projection_source=rad, 
                                            projection_target = wrl.georef.epsg_to_osr(25832)) # UTM Zone 33N: 25832, WGS: 4326


# Save grid information to files.
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
pl.xticks(ticks=[400000, 500000, 600000, 700000, 800000], fontsize=15)
pl.ylim(bottom=5300000)
pl.xlim(left=350000, right=800000)
pl.xlabel("Easting", fontsize=15)
pl.ylabel("Northing", fontsize=15)
pl.title('09-01-2019 12:00 UTC\nradar sites drs, umd, neu, eis, pro\nUTM Zone 33N (EPSG 25832)', fontsize=17)
pl.savefig(f"images/composite_{filename_drs[15:25]}_utm", dpi=600)



# Read gauge metadata.
# gauges_metadata = []
# file_data = open('geodata/RR_stations_150km_UTM.csv')
# for row in file_data:
#     gauges_metadata.append(row.split(";"))
    
# gauges_metadata = np.array(gauges_metadata)

# Create index list for gauges.
 
# Apply RADAR-gauge adjustment methods.

# Evaluate RADAR-gauge adjustment methods.