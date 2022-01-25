from sklearn.metrics import mean_squared_error

from func import max_from_arrays, plot_grid, plot_polar, cm_binary

def plot_adjusted_data(xgrid, ygrid, gaugedata, adjusted_add_arr, adjusted_mul_arr, adjusted_mulcon_arr, adjusted_mix_arr, minutes, filenameextension=""):
    """Plot adjusted radar data."""
    plot_grid(adjusted_add_arr, gaugedata, xgrid, ygrid, "Additive adjustment\n(spatially variable)", f"adjustment_add{filenameextension}", minutes, plotgauges=True)
    plot_grid(adjusted_mul_arr, gaugedata, xgrid, ygrid,"Multiplicative adjustment\n(spatially variable)", f"adjustment_mul{filenameextension}", minutes, plotgauges=True)
    plot_grid(adjusted_mulcon_arr, gaugedata, xgrid, ygrid,"Multiplicative adjustment\n(spatially uniform)", f"adjustment_mfb{filenameextension}", minutes, plotgauges=True)
    plot_grid(adjusted_mix_arr, gaugedata, xgrid, ygrid,"Additive-multiplicative-mixed adjustment\n(spatially variable)", f"adjustment_mixed{filenameextension}", minutes, plotgauges=True)
    return 0

def plot_adjust_errors(xgrid, ygrid, gaugedata, radar, adjusted_add_arr, adjusted_mul_arr, adjusted_mulcon_arr, adjusted_mix_arr, minutes):
    """Plot errors."""
    plot_grid(adjusted_add_arr - radar, gaugedata, xgrid, ygrid,"Additive error\n(spatially variable)", "adjustment_add_diff", minutes, plotgauges=True)
    plot_grid(adjusted_mul_arr - radar, gaugedata, xgrid, ygrid,"Multiplicative error\n(spatially variable)", "adjustment_mul_diff", minutes, plotgauges=True)
    plot_grid(adjusted_mulcon_arr - radar, gaugedata, xgrid, ygrid,"Multiplicative error\n(spatially uniform)", "adjustment_mfb_diff", minutes, plotgauges=True)
    plot_grid(adjusted_mix_arr - radar, gaugedata, xgrid, ygrid,"Additive-multiplicative-mixed error\n(spatially variable)", "adjustment_mixed_diff", minutes, plotgauges=True)    
    return 0


# # Cumulative distribution function of radar, gauges and adjustment methods.
# fig = pl.figure(figsize=(10, 6))
# # n_radar = plt.hist(np.round(radar_1d, decimals=1), 100, density=True, histtype="step", cumulative=True, label="raw radar", log=False, linewidth=1.5)
# # n_gauges = plt.hist(obs_1d, 100, density=True, histtype="step", cumulative=True, label="gauges", log=False, linewidth=1.5)
# # n_add = plt.hist(np.round(addadjusted, decimals=1), 100, density=True, histtype="step", cumulative=True, label="add (var)", log=False, linewidth=1.5)
# # n_mul = plt.hist(np.round(multadjusted, decimals=1), 100, density=True, histtype="step", cumulative=True, label="mul (var)", log=False, linewidth=1.5)
# # n_mulconst = plt.hist(np.round(mfbadjusted, decimals=1), 100, density=True, histtype="step", cumulative=True, label="mul (const)", log=False, linewidth=1.5)
# # n_mix = plt.hist(np.round(mixadjusted, decimals=1), 100, density=True, histtype="step", cumulative=True, label="mix (var)", log=False, linewidth=1.5)
# n_radar = plt.hist(radar_1d, 100, density=True, histtype="step", cumulative=False, label="raw radar", log=False, linewidth=1.5)
# n_gauges = plt.hist(obs_1d, 100, density=True, histtype="step", cumulative=False, label="gauges", log=False, linewidth=1.5)
# n_add = plt.hist(adjusted_add, 100, density=True, histtype="step", cumulative=False, label="add (var)", log=False, linewidth=1.5)
# n_mul = plt.hist(adjusted_mul, 100, density=True, histtype="step", cumulative=False, label="mul (var)", log=False, linewidth=1.5)
# n_mulconst = plt.hist(adjusted_mulcon, 100, density=True, histtype="step", cumulative=False, label="mul (const)", log=False, linewidth=1.5)
# n_mix = plt.hist(adjusted_mix, 100, density=True, histtype="step", cumulative=False, label="mix (var)", log=False, linewidth=1.5)
# plt.legend(loc="lower right")
# plt.grid()
# plt.xlim([-2, 4.5])
# # plt.ylim([0.4,1])
# plt.xlabel("Precipitation [mm]", fontsize=12)
# plt.ylabel("CDF", fontsize=12)
# plt.savefig("images/adjustment_eval", dpi=600)

# # Calculate RMSE.
# for x in [n_radar, n_add, n_mul, n_mulconst, n_mix]:
#     print(mean_squared_error(n_gauges[0], x[0], squared=True))