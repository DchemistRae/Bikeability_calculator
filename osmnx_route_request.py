import geopandas as gpd
import osmnx as ox
import pandas as pd
import numpy as np
# get route
orsgpd = gpd.read_file('ors_route.geojson', driver= 'GeoJSON')
#Convert CRS to meter type
orsgpd = orsgpd.to_crs(epsg=3395)
#Add small buffer of 1 meters
orsgpd['geometry'] = orsgpd.buffer(1)
# Revert CRS to original type
orsgpd =orsgpd.to_crs(epsg=4326)
orsgpd.plot()
# request data from osmnx
data = ox.graph_from_polygon(orsgpd.geometry.iloc[0])
ox.plot_graph(data)
nodes, edges = ox.graph_to_gdfs(data)

edges.plot()
edges.columns
# works!!!
#Add weightings as a new column length
edges['weight'] = edges.geometry.length

#edges.dtypes
# len(edges.name.unique().tolist())
#Convert variables of interest to proper data type

#edges.maxspeed = edges.maxspeed.fillna(0)
#edges.maxspeed = edges.maxspeed.astype(int)
maxspeed_map = {8:10, 10:10, 20:10, 30:9, 40:8, 50:7, 60:6, 70:5, 80:4, 90:3, 100:2, 110:1}
edges.maxspeed = edges["maxspeed"].map(maxspeed_map)
edges['maxspeed'] = pd.to_numeric(edges.maxspeed,errors='coerce', downcast='signed')
edges['lanes'] =pd.to_numeric(edges.lanes,errors='coerce', downcast='integer')
edges.oneway = edges.oneway.astype(int)
edges.name  = edges.name.astype(str)
#weighted mean excluding nan / function
def weighted_mean(arr_lst,wt_lst):
    indices = ~np.isnan(arr_lst)
    avg_wt = np.average(arr_lst[indices],weights=wt_lst[indices])
    return avg_wt

avg_maxspeed =weighted_mean(edges['maxspeed'],edges['weight'])
avg_nlanes = round(weighted_mean(edges.lanes,edges.weight))
avg_oneway = weighted_mean(edges.oneway,edges.weight) * 100


from geopy.distance import geodesic
>>> newport_ri = (41.49008, -71.312796)
>>> cleveland_oh = (41.499498, -81.695391)
>>> print(geodesic(newport_ri, cleveland_oh).miles)
