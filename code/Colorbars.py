from matplotlib.colors import LinearSegmentedColormap

# Used for rain depths plot.
cm = LinearSegmentedColormap.from_list("new_jet", [(1,1,1,0), (0,0.19,1), (0,0.69,1), (0.44,1,0.56), (1,1,0), (1,0.69,0), (1,0,0), (0.5,0,0)], N=45) 

# Used for clutter plot.
cm_clutter = LinearSegmentedColormap.from_list("cm_clutter", [(1,1,1,0), (1,0,0)], N=2) 

# Used for latest radar composite plot.
cm_latest = LinearSegmentedColormap.from_list("cm_latest", ["white", "white","royalblue","royalblue","royalblue","royalblue","royalblue","royalblue","royalblue","royalblue",
                                                          "cornflowerblue","cornflowerblue","cornflowerblue","cornflowerblue","cornflowerblue","cornflowerblue","cornflowerblue","cornflowerblue","cornflowerblue","cornflowerblue",                                                        
                                                          "skyblue","skyblue","skyblue","skyblue","skyblue","skyblue","skyblue","skyblue","skyblue","skyblue",
                                                          "paleturquoise","paleturquoise","paleturquoise","paleturquoise","paleturquoise","paleturquoise","paleturquoise","paleturquoise","paleturquoise","paleturquoise",
                                                          "darkgreen","darkgreen","darkgreen","darkgreen","darkgreen","darkgreen","darkgreen","darkgreen","darkgreen","darkgreen",
                                                          "limegreen","limegreen","limegreen","limegreen","limegreen","limegreen","limegreen","limegreen","limegreen","limegreen",
                                                          "lightgreen","lightgreen","lightgreen","lightgreen","lightgreen","lightgreen","lightgreen","lightgreen","lightgreen","lightgreen",
                                                          "yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow",
                                                          "gold","gold","gold","gold","gold","gold","gold","gold","gold","gold",
                                                          "orange","orange","orange","orange","orange","orange","orange","orange","orange","orange",
                                                          "tomato","tomato","tomato","tomato","tomato","tomato","tomato","tomato","tomato","tomato",
                                                          "red","red","red","red","red","red","red","red","red","red", 
                                                          "darkred","darkred","darkred","darkred","darkred","darkred","darkred","darkred","darkred","darkred",
                                                          "purple","purple","purple","purple","purple","purple","purple","purple","purple","purple",
                                                          "darkviolet","darkviolet","darkviolet","darkviolet","darkviolet","darkviolet","darkviolet","darkviolet","darkviolet","darkviolet",
                                                          "k","k","k","k","k","k","k","k","k","k"], N=160)