import datetime 
import matplotlib.pylab as pl
import wradlib as wrl
import numpy as np
import math
from scipy import stats
import shapefile as shp  # Requires the pyshp package
import matplotlib.pyplot as plt
from pyproj import Proj

from colorbars import cm


myProj = Proj("+proj=utm +zone=33 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

def metadata(filename):
    """ Return radar site abbreviation, radar site description and datetime object."""
    site_abb = filename[26:29]
    dt = datetime.datetime.strptime(filename[15:25], "%y%m%d%H%M")
    if site_abb == "drs":
        site_text = "DWD RADAR 10488 Dresden"
    elif site_abb == "pro":
        site_text = "DWD RADAR 10392 Prötzel"
    elif site_abb == "umd":
        site_text = "DWD RADAR 10356 Ummendorf"
    elif site_abb == "neu":
        site_text = "DWD RADAR 10557 Neuhaus"
    elif site_abb == "eis":
        site_text = "DWD RADAR 10780 Eisberg"
    else:
        print("station name not found")
    return site_abb, site_text, dt

def plot_polar(data, filename, subtitle, what, cm="viridis", cbarlabel = "Reflectivity (dBZ)", plot_cbar = True):
    """ Plot radar in polar coordinates."""
    site_abb, site_text, dt = metadata(filename)
    pl.figure(figsize=(10,8))
    ax, pm = wrl.vis.plot_ppi(data, cmap=cm)
    ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
    if plot_cbar == True:
        cbar = pl.colorbar(pm, shrink=0.75)
        cbar.set_label(cbarlabel)
    pl.xlim([-135, 135])
    pl.ylim([-135, 135])
    pl.title(f'{dt.strftime("%d-%m-%Y %H:%M")} UTC\n{site_text}\n{subtitle}', fontsize=11)
    pl.savefig(f"images/{site_abb}/radar_dx_{site_abb}_{filename[15:25]}_{what}.png", dpi=600)
    return 0


def clutter_gabella(data, filename):   
    """
    Identify clutter, remove clutter and interpolate data (algorithm by Gabella et al. (2002)).
    Plot clutter map and corrected radar image. Returns clutter map and clutter free data.
    """
    clmap = wrl.clutter.filter_gabella(data, wsize=5, thrsnorain=0., tr1=6., n_p=8, tr2=1.3)
    data_no_clutter = wrl.ipol.interpolate_polar(data, clmap)
    site_abb, site_text, dt = metadata(filename)
    return clmap, data_no_clutter    


def attcorr(data_no_clutter, filename):
    """Calculate integrated attenuation for each bin (Kraemer et al., 2008 and Jacobi et al., 2016)."""       
    site_abb, site_text, dt = metadata(filename)
    att = wrl.atten.correct_attenuation_constrained(data_no_clutter, 
                                                    a_max=1.67e-4, a_min=2.33e-5, n_a=100, b_max=0.7, b_min=0.65, n_b=6, # coefficients
                                                    gate_length=1., constraints=[wrl.atten.constraint_dbz, wrl.atten.constraint_pia],
                                                    constraint_args=[[59.0],[20.0]])
    data_attcorr = data_no_clutter + att
    return att, data_attcorr


def plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, bin):
    """Plot attenuation correction for single bins."""
    pl.figure(figsize=(10,8))
    pl.plot(data_no_clutter[bin], label="no AC", c="r", lw=1)
    pl.plot(data_attcorr[bin], label="with AC", c="g", lw=1)
    pl.xlabel("km", fontsize=14)
    pl.ylabel("dBZ", fontsize=14)
    pl.legend(fontsize=14)
    site_abb, site_text, dt = metadata(filename)
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\n{site_text}\nAC - azimuth angle {bin} degree', fontsize=14)
    pl.savefig(f"images/{site_abb}/radar_dx_{site_abb}_{filename[15:25]}_attcorr_bin{bin}.png", dpi=600)
    return 0


def plot_attenuation_mean_bin(data_no_clutter, data_attcorr, filename):
    """Plot attenuation correction for all bins averaged."""
    pl.figure(figsize=(10,8))
    pl.plot(np.mean(data_no_clutter, axis=1), label="no AC", c="r", lw=1)
    pl.plot(np.mean(data_attcorr, axis=1), label="AC done", c="g", lw=1)
    pl.xlabel("km", fontsize=14)
    pl.ylabel("dBZ", fontsize=14)
    pl.legend(fontsize=14)
    site_abb, site_text, dt = metadata(filename)
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\n{site_text}\nAC (averaged)', fontsize=14)
    pl.savefig(f"images/{site_abb}/radar_dx_{site_abb}_{filename[15:25]}_attcorr_meanbin.png", dpi=600)
    return 0


def rain_depths(data, filename, minutes):
    """ 
    Apply ZR-relation (a=200, b=1.6) to get precipitation rates.
    Integrate rainfall rates to rainfall depth.
    """
    R = wrl.zr.z_to_r(wrl.trafo.idecibel(data), a=200, b=1.6)
    depths = wrl.trafo.r_to_depth(R, minutes*60)
    return depths


def plot_raindepths(depths, filename, minutes):
    """Plot rain depths in polar coordinates."""
    pl.figure(figsize=(10, 9))
    ax, im = wrl.vis.plot_ppi(depths, cmap=cm, vmin=0)
    ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
    cbar = pl.colorbar(im, shrink=0.75)
    cbar.set_label(f"{minutes} min - rain depths (mm)", fontsize=14)
    cbar.ax.tick_params(labelsize=11) 
    pl.xlim([-135, 135])
    pl.ylim([-135, 135])
    ax.tick_params(axis='both', which='major', labelsize=11)
    site_abb, site_text, dt = metadata(filename)
    pl.title(f'{dt.strftime("%d-%m-%Y %H:%M")} UTC\n{site_text}\nAfter applying Z-R-relation', fontsize=11)
    pl.savefig(f"images/{site_abb}/radar_dx_{site_abb}_{filename[15:25]}_raindepths{minutes}min.png", dpi=600)
    return 0


def max_from_arrays(array1, array2):
    """Choose element wise maximum. Keeps NaN's as NaN's if both are NaN."""
    if array1.shape == array2.shape:
        newarray = np.zeros(array2.shape)
        for i in range(len(array1)):
            for j in range(len(array1[0])):
                val1 = array1[i][j]
                val2 = array2[i][j]
                newarray[i][j] = np.nanmax([val1, val2]);
    else:
        raise ValueError("Arrays' shape don't match.") 
    return newarray


def plot_grid(data, gaugedict, xgrid, ygrid, plottitle, filename, minutes, cmap=cm, plotgauges=False):
    """ Plot gridded data."""
    # replace negative numbers with zero.
    # data[data<0] = 0
    pl.figure(figsize=(10, 8))
    ax = pl.subplot(111, aspect="equal")
    # add radar data
    if minutes == 5:
        pm = ax.pcolormesh(xgrid, ygrid, data, cmap=cmap, vmin=0, vmax=0.35)
    if minutes == 60:
        pm = ax.pcolormesh(xgrid, ygrid, data, cmap=cmap, vmin=0, vmax=4.5)
    cbar = pl.colorbar(pm)
    cm.set_bad(color='gray')
    cbar.ax.tick_params(labelsize=14) 
    # cbar.set_label(f"{minutes} min - rain depths (mm)", fontsize=14)
    cbar.set_label(f"{minutes} min - Niederschlagshöhen (mm)", fontsize=14)
    # add gauge stations
    if plotgauges == True:
        pl.scatter(gaugedict['easting'], gaugedict["northing"],  marker='+', s=3, c="k", alpha=0.5)
    # add country shp
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
    pl.xlabel("Rechtswert (m)", fontsize=14)
    pl.ylabel("Hochwert (m)", fontsize=14)
    ax.ticklabel_format(useOffset=False, style='plain')
    ax.tick_params(axis='both', which='major', labelsize=14)
    pl.xlim(50000, 600000)
    pl.ylim(min(ygrid), 6000000)
    pl.grid(lw=0.5, zorder=10)
    pl.title(plottitle, fontsize=14)
    pl.savefig(f"images/{filename}{minutes}min", dpi=600, transparent=False)
    
def quantiles_100(liste):
    score_list = []
    liste = [x for x in liste if not np.isnan(x) ==True] # remove NaN's
    for x in np.arange(1,101,1):
        score_list.append(stats.scoreatpercentile(liste, x))
    return score_list