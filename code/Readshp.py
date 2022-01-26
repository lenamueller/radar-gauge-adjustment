import shapefile as shp
import matplotlib.pyplot as plt
from pyproj import Proj


filename = "geodata/DEU_adm1_multiline.shp"
sf = shp.Reader(filename)
myProj = Proj("+proj=utm +zone=33 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs") # target projection

plt.figure()
lines_seperated = []
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
        east, north = [], []
        for j in range(len(x)):
            e, n = myProj(x[j], y[j])
            east.append(e)
            north.append(n)
        plt.plot(east, north, lw=1, c="k")

plt.show()