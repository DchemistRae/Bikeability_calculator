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

#converted crs to meter type then i added 0.3 meter buffer(very thin)
frb = frb.to_crs(epsg=3395)
orsgpd = orsgpd.to_crs(epsg=3395)

frb['geometry'] = frb.buffer(0.3)
orsgpd['geometry'] = orsgpd.buffer(0.3)

#Merge both gdf using overlay
res_intersection = gpd.overlay(orsgpd, frb, how='intersection')
res_intersection.head()
res_intersection.plot(column='highway')

#Reproject joines gdf to original crs
res_intersection = res_intersection.to_crs(epsg=4326)

#Write to file
res_intersection.to_file('joineddata.geojson', driver='GeoJSON')










