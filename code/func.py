import matplotlib.pylab as pl
import wradlib as wrl
import wradlib.clutter as clutter
import numpy as np
from colorbar import cm


def plot_rawdata(data, dt, filename):
    """Plot reflectivity."""
    pl.figure(figsize=(10,8))
    ax, im = wrl.vis.plot_ppi(data, cmap="viridis") # proj="cg"
    ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
    cbar = pl.colorbar(im, shrink=0.75)
    cbar.set_label("Reflectivity (dBZ)")
    pl.xlim([-135, 135])
    pl.ylim([-135, 135])
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nraw data', fontsize=11)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_raw.png", dpi=600)
    return 0

def clutter_gabella(data, dt, filename):
    """Clutter identification by Gabella et al. (2002). Clutter removal and data interpolation."""
    clmap = clutter.filter_gabella(data, wsize=5, thrsnorain=0., tr1=6., n_p=8, tr2=1.3)
    pl.figure(figsize=(10,8))
    ax, pm = wrl.vis.plot_ppi(clmap)
    ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
    pl.xlim([-135, 135])
    pl.ylim([-135, 135])
    ax.set_title(f'Detected clutter at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nAfter clutter correction', fontsize=11)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_cluttermap.png")
    
    data_no_clutter = wrl.ipol.interpolate_polar(data, clmap)
    pl.figure(figsize=(10,8))
    ax, pm = wrl.vis.plot_ppi(data_no_clutter)
    ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
    cbar = pl.colorbar(pm, shrink=0.75)
    cbar.set_label("Reflectivity (dBZ)")
    pl.xlim([-135, 135])
    pl.ylim([-135, 135])
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nAfter clutter correction', fontsize=11)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_noclutter.png", dpi=600)
    return clmap, data_no_clutter

def attenuation_corr(data_no_clutter, dt, filename):
    """AC: Calculate integrated attenuation for each bin. Kraemer et al., 2008 and Jacobi et al., 2016"""       
    att = wrl.atten.correct_attenuation_constrained(data_no_clutter, 
                                                    a_max=1.67e-4, a_min=2.33e-5, n_a=100, b_max=0.7, b_min=0.65, n_b=6, # coefficients
                                                    gate_length=1.,  # 1km
                                                    constraints=[wrl.atten.constraint_dbz, wrl.atten.constraint_pia],
                                                    constraint_args=[[59.0],[20.0]])
    data_attcorr = data_no_clutter + att
    return att, data_attcorr

def attenuation_plots(data_no_clutter, att, data_attcorr, dt, filename):
    # radar plot with correction for each bin
    pl.figure(figsize=(10,8))
    ax, pm = wrl.vis.plot_ppi(data_attcorr)
    ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
    cbar = pl.colorbar(pm, shrink=0.75)
    cbar.set_label("Reflectivity (dBZ)")
    pl.xlim([-135, 135])
    pl.ylim([-135, 135])
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\n After attenuation correction', fontsize=11)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_attcorr.png", dpi=600)

    pl.figure(figsize=(10,8))
    ax, pm = wrl.vis.plot_ppi(att, cmap="Reds")
    ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
    cbar = pl.colorbar(pm, shrink=0.75)
    cbar.set_label("$\Delta$ Reflectivity (dBZ)")
    pl.xlim([-135, 135])
    pl.ylim([-135, 135])
    pl.title(f'$\Delta$ Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\n Attenuation error', fontsize=11)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_att.png", dpi=600)
    
    # line plot: mean bin
    pl.figure(figsize=(10,8))
    pl.plot(np.mean(data_no_clutter, axis=1), label="no AC", c="r", lw=1)
    pl.plot(np.mean(data_attcorr, axis=1), label="AC done", c="g", lw=1)
    pl.xlabel("km", fontsize=14)
    pl.ylabel("dBZ", fontsize=14)
    pl.legend(fontsize=14)
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nAC (averaged)', fontsize=14)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_attcorr_meanbin.png", dpi=600)
    
    # line plot: single bins
    pl.figure(figsize=(10,8))
    pl.plot(data_no_clutter[0], label="no AC", c="r", lw=1)
    pl.plot(data_attcorr[0], label="with AC", c="g", lw=1)
    pl.xlabel("km", fontsize=14)
    pl.ylabel("dBZ", fontsize=14)
    pl.legend(fontsize=14)
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nAC - azimuth angle 0 degree', fontsize=14)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_attcorr_bin0.png", dpi=600)
    
    pl.figure(figsize=(10,8))
    pl.plot(data_no_clutter[90], label="no AC", c="r", lw=1)
    pl.plot(data_attcorr[90], label="with AC", c="g", lw=1)
    pl.xlabel("km", fontsize=14)
    pl.ylabel("dBZ", fontsize=14)
    pl.legend(fontsize=14)
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nAC - azimuth angle 90 degree', fontsize=14)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_attcorr_bin90.png", dpi=600)
    
    pl.figure(figsize=(10,8))
    pl.plot(data_no_clutter[180], label="no AC", c="r", lw=1)
    pl.plot(data_attcorr[180], label="with AC", c="g", lw=1)
    pl.xlabel("km", fontsize=14)
    pl.ylabel("dBZ", fontsize=14)
    pl.legend(fontsize=14)
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nAC - azimuth angle 180 degree', fontsize=14)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_attcorr_bin180.png", dpi=600)
    
    pl.figure(figsize=(10,8))
    pl.plot(data_no_clutter[270], label="no AC", c="r", lw=1)
    pl.plot(data_attcorr[270], label="with AC", c="g", lw=1)
    pl.xlabel("km", fontsize=14)
    pl.ylabel("dBZ", fontsize=14)
    pl.legend(fontsize=14)
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nAC - azimuth angle 270 degree', fontsize=14)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_attcorr_bin270.png", dpi=600)
    
    pl.figure(figsize=(10,8))
    pl.plot(data_no_clutter[240], label="no AC", c="r", lw=1)
    pl.plot(data_attcorr[240], label="with AC", c="g", lw=1)
    pl.xlabel("km", fontsize=14)
    pl.ylabel("dBZ", fontsize=14)
    pl.legend(fontsize=14)
    pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nAC - azimuth angle 270 degree', fontsize=14)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_attcorr_bin240.png", dpi=600)
    
    return 0

def plot_raindepths(depths, dt, filename):
    """Plot rain depths."""
    pl.figure(figsize=(10, 8))
    ax, im = wrl.vis.plot_ppi(depths, cmap=cm)
    ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
    cbar = pl.colorbar(im, shrink=0.75)
    cbar.set_label("5 min - Rain depths (mm)")
    pl.xlim([-135, 135])
    pl.ylim([-135, 135])
    pl.title(f'5min - rain dephts at {dt.strftime("%d-%m-%Y %H:%M")} UTC\nDWD RADAR 10488 Dresden\nAfter applying Z-R-relation', fontsize=11)
    pl.savefig(f"images/radar_dx _drs_{filename[15:25]}_raindepths.png", dpi=600)
    return 0