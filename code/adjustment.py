import numpy as np
import matplotlib.pylab as pl
import wradlib.adjust as adjust
import wradlib.verify as verify
import wradlib.util as util


# Create grid axes and grid.
xgrid = np.arange(0, 10)
ygrid = np.arange(20, 30)
gridshape = len(xgrid), len(ygrid)
grid_coords = util.gridaspoints(ygrid, xgrid)

# Radar data
radar = np.zeros((700*700)) # 1D array (n numbers)

# Gauge data
num = 10 # number of gauges
obs_ix = np.zeros((num)) # 1D-array of gauge placements (indices)
obs_coords = grid_coords[obs_ix] # 2D-array of gauge placements (grid coords)
truth = np.zeros((700*700)) # 1D-array of gauge data
obs = truth[obs_ix] # 1D-array with selected values

# adjustment methods
mfbadjuster = adjust.AdjustMFB(obs_coords, grid_coords)
mfbadjusted = mfbadjuster(obs, radar)
addadjuster = adjust.AdjustAdd(obs_coords, grid_coords)
addadjusted = addadjuster(obs, radar)
multadjuster = adjust.AdjustMultiply(obs_coords, grid_coords)
multadjusted = multadjuster(obs, radar)


def gridplot(data, title):
    """Quick and dirty helper function to produce a grid plot"""
    xplot = np.append(xgrid, xgrid[-1] + 1.) - 0.5
    yplot = np.append(ygrid, ygrid[-1] + 1.) - 0.5
    ax.pcolormesh(xplot, yplot, data.reshape(gridshape), vmin=0, vmax=maxval)
    ax.scatter(obs_coords[:, 0], obs_coords[:, 1], c=obs.ravel(),
               marker='s', s=50, vmin=0, vmax=maxval)
    #pl.colorbar(grd, shrink=0.5)
    pl.title(title)

def scatterplot(x, y, title=""):
    """Quick and dirty helper function to produce scatter plots"""
    pl.scatter(x, y)
    pl.plot([0, 1.2 * maxval], [0, 1.2 * maxval], '-', color='grey')
    pl.xlabel("True rainfall (mm)")
    pl.ylabel("Estimated rainfall (mm)")
    pl.xlim(0, maxval + 0.1 * maxval)
    pl.ylim(0, maxval + 0.1 * maxval)
    pl.title(title)


# Maximum value (used for normalisation of colorscales)
maxval = np.max(np.concatenate((truth, radar, obs, addadjusted)).ravel())

# Plot data
fig = pl.figure(figsize=(10, 6))
ax = fig.add_subplot(231, aspect='equal')
gridplot(truth, 'True rainfall')
ax = fig.add_subplot(232, aspect='equal')
gridplot(radar, 'Radar rainfall')
ax = fig.add_subplot(234, aspect='equal')
gridplot(mfbadjusted, 'Adjusted (MFB)')
ax = fig.add_subplot(235, aspect='equal')
gridplot(addadjusted, 'Adjusted (Add.)')
ax = fig.add_subplot(236, aspect='equal')
gridplot(multadjusted, 'Adjusted (Mult.)')
pl.tight_layout()
pl.savefig("adjustment_data")

# Plot verification
fig = pl.figure(figsize=(6, 6))
ax = fig.add_subplot(221, aspect='equal')
scatterplot(truth, radar, 'Radar vs. Truth (red: Gauges)')
pl.plot(obs, radar[obs_ix], linestyle="None", marker="o", color="red")
ax = fig.add_subplot(222, aspect='equal')
scatterplot(truth, mfbadjusted, 'Adjusted (MFB) vs. Truth')
ax = fig.add_subplot(223, aspect='equal')
scatterplot(truth, addadjusted, 'Adjusted (Add.) vs. Truth')
ax = fig.add_subplot(224, aspect='equal')
scatterplot(truth, multadjusted, 'Adjusted (Mult.) vs. Truth')
pl.tight_layout()
pl.savefig("adjustment_veri")
