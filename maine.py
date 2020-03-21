import numpy as np
import requests,json
import geopandas as gpd
import osmnx as ox
import pandas as pd
import random
import shapely
from evaluate_helpers import weighted_avgfunc, weighted_mean

class Create_data:

    def create_df(self):
        self.df = pd.DataFrame(columns=('distance', 'duration', 'surface_type','waycategory',
        'waytypes','steepness','suitability','maxspeed','lanes','oneway','connection'))

    def __init__(self, coords, ors_key):
        body = {"coordinates":coords,"attributes":["avgspeed","detourfactor",
            "percentage"],"extra_info":["steepness","suitability","surface","waytype",
            "waycategory","countryinfo"],"maneuvers":"true","preference":"recommended","roundabout_exits":"true",
            "continue_straight":"false","instructions":"true","instructions_format":"text"}
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': ors_key}
        call = requests.post('https://api.openrouteservice.org/v2/directions/cycling-regular/geojson', json=body,
                    headers=headers)
            
        #print(call.status_code, call.reason)
        #print(call.text)
        ans = call.json()

        with open("ors_route.geojson", "w") as file:
            json.dump(ans, file, indent=4)

            
        #Extracting json data into groups
        propties = (ans['features'][0]['properties'])
        extras =propties['extras']
        distance =propties['summary']['distance']
        duration =propties['summary']['duration']
        surface_type = extras['surface']['summary']
        waycategory = extras['waycategory']['summary']
        waytypes = extras['waytypes']['summary']
        steepness = extras['steepness']['summary']
        suitability = extras['suitability']['summary']
            
        #Result extraction
        self.distance = distance
        self.duration = duration
        self.wt_surface_type_avg = weighted_avgfunc(surface_type)
        self.wt_category_avg = weighted_avgfunc(waycategory)
        self.wt_waytypes_avg = weighted_avgfunc(waytypes)
        self.wt_steep_avg = weighted_avgfunc(steepness)
        self.wt_suitability_avg = weighted_avgfunc(suitability)
   
    def get_oxroute(self):
        # get route
        orsgpd = gpd.read_file('ors_route.geojson', driver= 'GeoJSON')
        #Convert CRS to meter type
        orsgpd = orsgpd.to_crs(epsg=3395)
        #Add small buffer of 1 meters
        orsgpd['geometry'] = orsgpd.buffer(1)
        # Revert CRS to original type
        orsgpd =orsgpd.to_crs(epsg=4326)
        #orsgpd.plot()
        # request data from osmnx
        data = ox.graph_from_polygon(orsgpd.geometry.iloc[0])
        #ox.plot_graph(data)
        nodes,edges = ox.graph_to_gdfs(data)
        #Add weightings as a new column length
        edges['weight'] = edges.geometry.length
        #Convert variables of interest to proper data type
        edges['maxspeed'] = pd.to_numeric(edges.maxspeed,errors='coerce', downcast='integer')
        edges['lanes'] =pd.to_numeric(edges.lanes,errors='coerce', downcast='integer')
        edges.oneway = edges.oneway.astype(int)
        edges.name  = edges.name.astype(str)
        #weighted mean excluding nan / function

        self.avg_maxspeed = round(weighted_mean(edges['maxspeed'],edges['weight']))
        self.avg_nlanes = round(weighted_mean(edges.lanes,edges.weight))
        self.avg_oneway = round(weighted_mean(edges.oneway,edges.weight))
        self.street_connections = len(edges.name.unique().tolist())

    def fill_df(self):
        self.df = self.df.append({
        "distance": self.distance,
        "duration": self.duration,
        "surface_type": self.wt_surface_type_avg,
        "waycategory": self.wt_category_avg,
        "waytypes": self.wt_waytypes_avg,
        "steepness": self.wt_steep_avg,
        "suitability": self.wt_suitability_avg,
        "maxspeed": self.avg_maxspeed,
        "lanes": self.avg_nlanes,
        "oneway": self.avg_oneway,
        "connection":self.street_connections
        }, ignore_index=True)
        return self.df

    def _create_origin_destination_df(self,city_name, n_coords):
        boundary = ox.gdf_from_place(city_name)
        # if boundary is point not polygon try again with which_result = 2
        if not type(boundary.iloc[0].geometry) is shapely.geometry.polygon.Polygon:
            boundary = ox.gdf_from_place(city_name, which_result=2)

        print('Download Footrpint data for ' + city_name)
        buildings = ox.footprints.footprints_from_polygon(polygon=boundary.iloc[0].geometry, retain_invalid=False)  
        
        coords_list = []
        for i in range(n_coords):

            start_n = random.randint(1, len(buildings))
            start_x = buildings.iloc[start_n].geometry.centroid.x
            start_y = buildings.iloc[start_n].geometry.centroid.y

            end_n = random.randint(1, len(buildings))
            end_x = buildings.iloc[end_n].geometry.centroid.x
            end_y = buildings.iloc[end_n].geometry.centroid.y
            self.coords_list =coords_list.append([[start_x, start_y], [end_x,end_y]])
        return self.coords_list

        
