from matplotlib.colors import LinearSegmentedColormap


cm = LinearSegmentedColormap.from_list("new_jet", [(1,1,1,0), (0,0.19,1), (0,0.69,1), (0.44,1,0.56), (1,1,0), (1,0.69,0), (1,0,0), (0.5,0,0)], N=45) 
cm_binary = LinearSegmentedColormap.from_list("new_jet", [(1,1,1,0), (1,0,0)], N=2) 