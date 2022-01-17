import datetime 
import matplotlib.pylab as pl
import wradlib as wrl
import numpy as np

from colorbar import cm, cm_binary


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


def plot_radar(data, filename, subtitle, what, cm="viridis", cbarlabel = "Reflectivity (dBZ)", plot_cbar = True):
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
    pl.savefig(f"images/radar_dx_{site_abb}_{filename[15:25]}_{what}.png", dpi=600)
    return 0


def clutter_gabella(data, filename):   
    """
    Identify clutter, remove clutter and interpolate data (algorithm by Gabella et al. (2002)).
    Plot clutter map and corrected radar image. 
    Returns clutter map and clutter free data.
    """
    clmap = wrl.clutter.filter_gabella(data, wsize=5, thrsnorain=0., tr1=6., n_p=8, tr2=1.3)
    data_no_clutter = wrl.ipol.interpolate_polar(data, clmap)
    site_abb, site_text, dt = metadata(filename)
    plot_radar(data=clmap, filename=filename, what="cluttermap", subtitle="Detected clutter", cm=cm_binary, plot_cbar=False)
    plot_radar(data=data_no_clutter, filename=filename, what="noclutter", subtitle="After clutter correction")    
    return clmap, data_no_clutter    


def attcorr(data_no_clutter, filename):
    """Calculate integrated attenuation for each bin (Kraemer et al., 2008 and Jacobi et al., 2016)."""       
    site_abb, site_text, dt = metadata(filename)
    att = wrl.atten.correct_attenuation_constrained(data_no_clutter, 
                                                    a_max=1.67e-4, a_min=2.33e-5, n_a=100, b_max=0.7, b_min=0.65, n_b=6, # coefficients
                                                    gate_length=1., constraints=[wrl.atten.constraint_dbz, wrl.atten.constraint_pia],
                                                    constraint_args=[[59.0],[20.0]])
    data_attcorr = data_no_clutter + att
    plot_radar(data=att, filename=filename, subtitle="Attenuation error", what="att", cm="Reds", cbarlabel="$\Delta$ Reflectivity (dBZ)")
    plot_radar(data=data_attcorr, filename=filename, subtitle="After attenuation correction", what="attcorr")
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
    pl.savefig(f"images/radar_dx_{site_abb}_{filename[15:25]}_attcorr_bin{bin}.png", dpi=600)
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
    pl.savefig(f"images/radar_dx_{site_abb}_{filename[15:25]}_attcorr_meanbin.png", dpi=600)
    return 0


def plot_raindepths(depths, filename):
    """Plot rain depths in polar coordinates."""
    pl.figure(figsize=(10, 8))
    ax, im = wrl.vis.plot_ppi(depths, cmap=cm)
    ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
    cbar = pl.colorbar(im, shrink=0.75)
    cbar.set_label("5 min - rain depths (mm)")
    pl.xlim([-135, 135])
    pl.ylim([-135, 135])
    site_abb, site_text, dt = metadata(filename)
    pl.title(f'{dt.strftime("%d-%m-%Y %H:%M")} UTC\n{site_text}\nAfter applying Z-R-relation', fontsize=11)
    pl.savefig(f"images/radar_dx_{site_abb}_{filename[15:25]}_raindepths.png", dpi=600)
    return 0


def rain_depths(data, filename, duration_sec=300):
    """ 
    Apply ZR-relation (a=200, b=1.6) to get precipitation rates.
    Integrate rainfall rates to rainfall depth (default: 300sec).
    """
    R = wrl.zr.z_to_r(wrl.trafo.idecibel(data))
    depths = wrl.trafo.r_to_depth(R, duration_sec)
    plot_raindepths(depths, filename)
    return depths


def plot_gridded(xgrid, ygrid, gridded, filename, subtitle, proj_src, proj_trg_epsgno = 25832):
    """Plot gridded field with defined epsg number."""
    xgrid, ygrid = wrl.georef.reproject(xgrid, ygrid, projection_source=proj_src, projection_target = wrl.georef.epsg_to_osr(proj_trg_epsgno))
    pl.figure(figsize=(10, 8))
    ax = pl.subplot(111, aspect="equal")
    pm = pl.pcolormesh(xgrid, ygrid, gridded, cmap=cm, vmax=0.3)
    cbar = pl.colorbar(pm, shrink=0.75)
    cbar.ax.tick_params(labelsize=15) 
    cbar.set_label("5 min - rain depths (mm)", fontsize=15)
    pl.xticks(ticks=[400000, 500000, 600000, 700000, 800000], fontsize=15)
    pl.yticks(fontsize=15)
    pl.xlabel("Easting (m)", fontsize=15)
    pl.ylabel("Northing (m)", fontsize=15)
    pl.ylim(bottom=5300000)
    pl.xlim(right=800000)
    pl.grid()
    site_abb, site_text, dt = metadata(filename)
    pl.title(f'{dt.strftime("%d-%m-%Y %H:%M")} UTC\n{site_text}\n{subtitle}', fontsize=17)
    pl.savefig(f"images/radar_dx_{site_abb}_{filename[15:25]}_grid_utm.png", dpi=600)    
    print(filename, np.nanmax(gridded))
    return 0


def get_depths(filename):
    """Read data from file. Correct clutter and attenuation. Calculate and return 5min - rain depths as (360   ,128) - array."""
    f = wrl.util.get_wradlib_data_file('example_data/'+filename)
    data, metadata = wrl.io.read_dx(f)
    plot_radar(data, filename, "Raw data", "raw")
    clmap, data_no_clutter = clutter_gabella(data, filename)
    att, data_attcorr = attcorr(data_no_clutter, filename)
    plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, 0)
    plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, 90)
    plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, 180)
    plot_attenuation_per_bin(data_no_clutter, data_attcorr, filename, 270)
    plot_attenuation_mean_bin(data_no_clutter, data_attcorr, filename)
    depths = rain_depths(data_attcorr, filename, 300)
    plot_raindepths(depths, filename)    
    return depths


def get_coords(depths, radar_loc, centerxy):
    """Project polar coordinates into a global xyz cartesian coordinates and grid data."""
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


def blending_radar_domains(domain, gridded_data):
    """Change nan's to zeros. Choose element wise maximum."""
    return np.maximum(domain, np.nan_to_num(gridded_data))