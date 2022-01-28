import shapefile as shp
from pyproj import Proj
import numpy as np


def read_boundary(shp_file, xgrid, ygrid):
    sf = shp.Reader(shp_file)
    myProj = Proj("+proj=utm +zone=33 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs") # target projection
    lines_seperated = []
    east, north = [], []
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
            for j in range(len(x)):
                e, n = myProj(x[j], y[j])
                east.append(e)
                north.append(n)
    # Access pixel indices.
    x_i = []
    y_i = []
    for i in range(len(east)):
        east_new = min(xgrid, key=lambda x:abs(x-east[i])) # Get closest pixel in xgrid/ygrid.
        north_new = min(ygrid, key=lambda x:abs(x-north[i]))
        x_i.append(list(xgrid).index(east_new))
        y_i.append(list(ygrid).index(north_new))
    boundaryarr = np.zeros([700,700])
    for i in range(len(x_i)):
        boundaryarr[y_i[i]][x_i[i]] = 1
        
    return east, north, boundaryarr