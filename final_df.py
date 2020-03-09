import numpy as np
import requests, json
import geopandas as gpd
import osmnx as ox
import pandas as pd
import numpy as np

def route_df(points, ors_key):
    ''' Create dataframe out
     of ors and osmnx data '''

    body = {"coordinates":points,"attributes":["avgspeed","detourfactor",
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
    #segments = propties['segments'][0]
    distance =propties['summary']['distance']
    duration =propties['summary']['duration']
    surface_type = extras['surface']['summary']
    waycategory = extras['waycategory']['summary']
    waytypes = extras['waytypes']['summary']
    steepness = extras['steepness']['summary']
    suitability = extras['suitability']['summary']
    #connectivity = segments['steps']
    
    
    #Function for weighted average for routes with more that one connection
    def weighted_avgfunc(var):
            var_wt =[]
            var_lst = []
            for x in range(len(var)):
                var_lst.append(var[x]['value'])
            for y in range(len(var)):
                var_amt = (var[y]['amount'])/100
                var_wt.append(var_amt)
            wt_var_avg =np.average(var_lst,weights=var_wt)
            return wt_var_avg

    #Result extraction
    try:
        distance != 0
    except LookupError as e:
        print(e)
    else:
        pass
        
    try:
        duration != 0
    except LookupError as e:
        print(e)
    else:
        pass
        
        
    try:
        surface_type != 0
    except LookupError as e:
        print(e)
    else:
        wt_surface_type_avg = weighted_avgfunc(surface_type)
        #print('weighted average surface type ={}'.format(wt_surface_type_avg))
          
    try:
        waycategory != 0
    except LookupError as e:
        print(e)
    else:
        wt_category_avg = weighted_avgfunc(waycategory)
        #print('weighted average road category = {}'.format(wt_category_avg))
        
    try:
        waytypes != 0
    except LookupError as e:
        print(e)
    else:
        wt_waytypes_avg = weighted_avgfunc(waytypes)
        #print('weighted average waytype = {}'.format(wt_waytypes_avg))
        
    try:
        steepness != 0
    except LookupError as e:
        print(e)
    else:
        wt_steep_avg = weighted_avgfunc(steepness)
        #print('weighted average steepness = {}'.format(wt_steep_avg))
        
    try:
        suitability != 0
    except LookupError as e:
        print(e)
    else:
        wt_suitability_avg = weighted_avgfunc(suitability)
        #print('weighted average suitability = {}'.format(wt_suitability_avg))
    
    
    #OSMNX data

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
    def weighted_mean(arr_lst,wt_lst):
        indices = ~np.isnan(arr_lst)
        avg_wt = np.average(arr_lst[indices],weights=wt_lst[indices])
        return avg_wt

    avg_maxspeed = round(weighted_mean(edges['maxspeed'],edges['weight']))
    avg_nlanes = round(weighted_mean(edges.lanes,edges.weight))
    avg_oneway = round(weighted_mean(edges.oneway,edges.weight))
    street_connections = len(edges.name.unique().tolist())
    #Create a final dataframe
    df = pd.DataFrame(columns=('distance', 'duration', 'surface_type','waycategory',
    'waytypes','steepness','suitability','maxspeed','lanes','oneway','connection'))
    #Populate dataframe
    df = df.append({
     "distance": distance,
     "duration": duration,
     "surface_type": wt_surface_type_avg,
     "waycategory": wt_category_avg,
     "waytypes": wt_waytypes_avg,
     "steepness": wt_steep_avg,
     "suitability": wt_suitability_avg,
     "maxspeed": avg_maxspeed,
     "lanes": avg_nlanes,
     "oneway": avg_oneway,
     "connection":street_connections
      }, ignore_index=True)
    return df



stuttgart_airport =[[9.19515,48.690494],[7.850182, 47.99501]]
points = [[7.854559, 48.003247],[7.850182, 47.99501]]
ors_key = '5b3ce3597851110001cf6248480fc21010a54f35ad5e49b6d97490fb'
route_df(points,ors_key)

