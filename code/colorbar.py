from matplotlib.colors import LinearSegmentedColormap


# define colors (list of RGB tuples: left blue, right red)
colors = [(0,0.19,1), (0,0.69,1), (0.44,1,0.56), (1,1,0), (1,0.69,0), (1,0,0), (0.5,0,0)]

# Create colormap with 150 bins: few bins > discrete colorbar
cm = LinearSegmentedColormap.from_list("new_jet", colors, N=150) 