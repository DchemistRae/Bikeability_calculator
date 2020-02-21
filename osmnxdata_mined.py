import osmnx as ox
from shapely.geometry import LineString
from descartes import PolygonPatch
import pandas as pd
import geopandas as gpd
import fiona


#Place of interest
place = 'Freiburg, baden württemberg, Germany'

#construct street network 
#fr = ox.graph_from_place(place, network_type='all')
#fig, ax= ox.plot_graph(fr)

#save road network as shapefile
#ox.save_graph_shapefile(fr, filename='network')

#Load shapefile as geopanda dataframe
frb = gpd.read_file("edges.shp", driver="shapefile")
#preview
frb.plot(column='highway')

#Load ors route
orsgpd = gpd.read_file('ors_route.geojson', driver= 'GeoJSON')
orsgpd.plot()
#Perform spatial join
geodf = gpd.sjoin(orsgpd, frb, how="inner", op='intersects')
geodf.shape
geodf.describe








