import geopandas as gpd
import osmnx as ox
# get route
orsgpd = gpd.read_file('ors_route.geojson', driver= 'GeoJSON')
orsgpd.geometry = orsgpd.geometry.buffer(0.0001)
orsgpd.plot()
# request data from osmnx
data = ox.graph_from_polygon(orsgpd.geometry.iloc[0])
ox.plot_graph(data)
nodes, edges = ox.graph_to_gdfs(data)

edges.plot()
edges.columns
# works!!!