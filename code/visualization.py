import datetime
import wradlib as wrl
import matplotlib.pylab as pl

# Read data.
fpath = 'weather/radar/sites/dx/drs/raa00-dx_10488-2112191750-drs---bin'
f = wrl.util.get_wradlib_data_file(fpath)
data, metadata = wrl.io.read_dx(f)
print("data shape:", data.shape, "metadata:", metadata.keys())

# Get date and time.
dt = datetime.datetime.strptime(fpath[42:52], "%y%m%d%H%M")

# Plot radar domain.
pl.figure(figsize=(10, 8))
ax, im = wrl.vis.plot_ppi(data, cmap="viridis") # proj="cg"
ax = wrl.vis.plot_ppi_crosshair((0,0,0), ranges=[20,40,60,80,100,120,128])
cbar = pl.colorbar(im, shrink=0.75)
cbar.set_label("Reflectivity (dBZ)")
pl.title(f'Reflectivity at {dt.strftime("%d-%m-%Y %H:%M")}\nDWD radar Dresden')
pl.xlim((-128,128))
pl.ylim((-128,128))
pl.savefig(f"images/radar_drs_{fpath[42:52]}.png")