import numpy as np
import requests,json
import geopandas as gpd
import osmnx as ox
import pandas as pd
from geopy.distance import geodesic

from evaluate_helpers import weighted_avgfunc, weighted_mean


def route_df(coords, ors_key):
    ''' Create dataframe out
     of ors and osmnx data '''

    waytype_map = {1:5, 2:5, 3:9, 4:7, 5:7, 6:10, 7:5, 8:1, 9:1, 10:2}
    surface_map = {1:10, 2:8, 3:10, 4:10, 5:5, 6:6, 7:4, 8:10, 9:9,
                10:7, 11:6, 12:7, 13:2, 14:7, 15:4, 16:2, 17:5}
    steepness_map = {-5:5, -4:7, -3:9, -2:10, -1:10, 0:10, 1:9, 2:7, 3:5, 4:2, 5:1}
    maxspeed_map = {8:10, 10:10, 20:10, 30:9, 40:8, 50:7, 60:6, 70:5, 80:4, 90:3, 100:2, 110:1}
    lanes_map = {1:10, 2:9, 3:5, 4:5, 5:3, 6:3, 7:2, 8:1}
    connections_map = {1.0:10, 1.1:9, 1.2:8, 1.3:7, 1.4:6, 1.5:5, 1.6:4, 1.7:3, 1.8:2, 1.9:1}
    oneway_map = {0:5, 1:10}

    df = pd.DataFrame(columns=('distance', 'duration', 'surface_type',
        'waytypes','steepness','suitability','maxspeed','lanes','oneway'))
  
    for i in range(len(coords)):

        print("Starting ORS route request....")
        body = {"coordinates":coords[i],"attributes":["avgspeed","detourfactor",
            "percentage"],"extra_info":["steepness","suitability","surface","waytype",
            "waycategory","countryinfo"],"maneuvers":"true","preference":"recommended","roundabout_exits":"true",
            "continue_straight":"false","instructions":"true","instructions_format":"text"}
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': ors_key}
        call = requests.post('https://api.openrouteservice.org/v2/directions/cycling-regular/geojson', json=body,
                    headers=headers)
            
        ans = call.json()

        with open("ors_route.geojson", "w") as file:
            json.dump(ans, file, indent=4)

            
        #Extracting json data into groups
        propties = (ans['features'][0]['properties'])
        extras =propties['extras']
        #segments = propties['segments'][0]
        distance =propties['summary']['distance']
        duration =propties['summary']['duration']
        surface_type = extras['surface']['summary']
        #waycategory = extras['waycategory']['summary']
        waytypes = extras['waytypes']['summary']
        steepness = extras['steepness']['summary']
        suitability = extras['suitability']['summary']
        #connectivity = segments['steps']
        start,end = coords[i]
        crowdistance = geodesic(end, start).meters #As crow flies distance
        directness = round(distance/crowdistance, 1)

        #map surface, waytype and steepness to numbers 1(worst) to 10(best) and 0(unknown)  
        
        directness = connections_map.get(directness,1)
        for ways in waytypes:
            ways['value'] = waytype_map.get(ways['value'],ways['value'])

        for surface in surface_type:
            surface['value'] = surface_map.get(surface['value'],surface['value'])
        
        for steep in steepness:
            steep['value'] = steepness_map.get(steep['value'],steep['value'])

        
        #Result extraction
        wt_surface_type_avg = weighted_avgfunc(surface_type)
        #wt_category_avg = weighted_avgfunc(waycategory)
        wt_waytypes_avg = weighted_avgfunc(waytypes)
        wt_steep_avg = weighted_avgfunc(steepness)
        wt_suitability_avg = weighted_avgfunc(suitability)
        
        #OSMNX data
        print('Starting OSMNX route service....')
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
        nodes, edges = ox.graph_to_gdfs(data)
        #Add weightings as a new column length
        edges['weight'] = edges.geometry.length

        #Convert variables of interest to proper data type
        try:
            edges['maxspeed'] = pd.to_numeric(edges.maxspeed,errors = 'coerce',downcast='integer')
        except AttributeError as e:
            print(e)
        finally:
                pass
        
        try:
            edges['lanes'] =pd.to_numeric(edges.lanes,errors='coerce', downcast='integer')
        except AttributeError as e:
            print(e)
        finally:
            pass
        edges.oneway = edges.oneway.astype(int)
        edges.name  = edges.name.astype(str)
        #street_connections = round(len(edges.name.unique().tolist())/distance)

        #replace values assigning weight 1 to 10
        try:
            edges.maxspeed = edges["maxspeed"].map(maxspeed_map)
        except KeyError as e:
            print(e)
        finally:
            pass
        
        try:
            edges.lanes = edges["lanes"].map(lanes_map)
        except KeyError as e:
            print(e)
        finally:
            pass
        edges.oneway = edges['oneway'].map(oneway_map)


        #weighted mean excluding nan / function
        try:
            avg_maxspeed = round(weighted_mean(edges['maxspeed'],edges['weight']))
        except AttributeError as e:
            print(e)
        finally:
            pass
        try:
            avg_nlanes = round(weighted_mean(edges.lanes,edges.weight))
        except AttributeError as e:
            print(e)
        finally:
            pass
        
        avg_oneway = round(weighted_mean(edges.oneway,edges.weight))
        

        #Populate dataframe
        df = df.append({
        "distance": distance,
        "duration": duration,
        "surface_type": wt_surface_type_avg,
        #"waycategory": wt_category_avg,
        "waytypes": wt_waytypes_avg,
        "steepness": wt_steep_avg,
        "suitability": wt_suitability_avg,
        "maxspeed": avg_maxspeed,
        "lanes": avg_nlanes,
        "oneway": avg_oneway,
        "directness":directness
        }, ignore_index=True)

    return df
    





