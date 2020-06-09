import geopandas as gpd
from shapely.geometry import Polygon, Point
import numpy as np
import osmnx as ox 

place_name = 'Berlin, Germany'
area = ox.gdf_from_place(place_name)

#Create grids
xmin,ymin,xmax,ymax = area.total_bounds #x = lon, y = lat


cols = np.linspace(ymin, ymax, num=6)
rows = np.linspace(xmin, xmax, num=6)

cell_centers = []
for x in rows:
    for y in cols:
        p =Point(x,y)
        if p.within(area.geometry.iloc[0]) == True:
            cell_centers.append([x,y])
        
        
        
        gls.append(p)
        ls.append((cell_centers[i]))
        cell_centers.append([x,y])

for i in range(len(cell_centers)):
    p = Point(cell_centers[i])


ls = []
gls = []
for i in range(len(cell_centers)):
    p = Point(cell_centers[i])
    if p.within(area.geometry.iloc[0]) == True:
        ls.append((polygons[i].centroid.x, polygons[i].centroid.y))
        gls.append(p)
        ls.append((cell_centers[i]))
        print({'True':i+1})
    else: print({'False':i+1})



height = 0.05
width = 0.05
rows = int(np.ceil((ymax-ymin) /  height))
cols = int(np.ceil((xmax-xmin) / width))
XleftOrigin = xmin
XrightOrigin = xmin + width
YtopOrigin = ymax
YbottomOrigin = ymax- height
polygons = []
for i in range(cols):
    Ytop = YtopOrigin
    Ybottom =YbottomOrigin
    for j in range(rows):
        polygons.append(Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)])) 
        Ytop = Ytop - height
        Ybottom = Ybottom - height
    XleftOrigin = XleftOrigin + width
    XrightOrigin = XrightOrigin + width


grid = gpd.GeoDataFrame({'geometry':polygons})
grid.crs = {'init': 'epsg:4326', 'no_defs': True}
grid =grid.to_crs(epsg=4326)
grid.to_crs(epsg=4839)
grid.plot()


ls = []
gls = []
for i in range(len(polygons)):
    p = Point(polygons[i].centroid.x, polygons[i].centroid.y)
    if p.within(area.geometry.iloc[0]) == True:
        gls.append(p)
        ls.append((polygons[i].centroid.x, polygons[i].centroid.y))
        print({'True':i+1})
    else: print({'False':i+1})







graph = ox.graph_from_place(place_name)
fig, ax = ox.plot_graph(graph)
(polygons[0].area * 6)/1e+6
grid['geometry'].to_crs({'init': 'epsg:3395'})\
               .map(lambda p: p.area / 10**6)

x, y = polygons[0].exterior.coords.xy
list(polygons[0].centroid.coords)
polygons[0].centroid.wkt



length = 0.1
wide = 0.1
ncols = np.ceil((ymax - ymin)/length)
nrows = np.ceil((xmax - xmin)/wide)
cols = np.linspace(ymin, ymax, num=int(ncols))
rows = np.linspace(xmin, xmax, num=int(nrows))



from shapely.geometry import shape
geom = shape(cell_centers)
b =gpd.GeoDataFrame({'geometry':geom}, index=[0])


cols = np.arange(ymin, ymax+0.00001, length)
rows = np.arange(xmin, xmax+0.00001, wide)

polygons = []
for x in cols:
    for y in rows:
        polygons.append( Polygon([(x,y), (x+wide, y), (x+wide, y-length), (x, y-length)]) )

    
cols = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), wide))
rows = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), length))
rows.reverse()


cols = np.linspace(ymin, ymax, num=5)
rows = np.linspace(xmin, xmax, num=5)

#Convert projection to meter to get appropriate grid sizes
area.crs ={'init': 'epsg:4326', 'no_defs': True}
area =area.to_crs(epsg=4839)
area =area.to_crs(epsg=4326)
