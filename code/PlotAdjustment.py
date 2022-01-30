from sklearn.metrics import mean_squared_error

from func import plot_grid


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