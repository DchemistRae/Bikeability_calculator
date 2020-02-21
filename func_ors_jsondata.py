# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 21:52:46 2019

@author: Dchemist_rae
"""
import numpy as np
import requests, json
def dat_extract(points,ors_key):
    '''Functions to extract
    important data from ORS query'''
    
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
    with open("ans.json", "w") as file:
        json.dump(ans, file, indent=4)

     
    #Extracting json data into groups
    propties = (ans['features'][0]['properties'])
    extras =propties['extras']
    segments = propties['segments'][0]
    distance =propties['summary']['distance']
    duration =propties['summary']['duration']
    surface_type = extras['surface']['summary']
    waycategory = extras['waycategory']['summary']
    waytypes = extras['waytypes']['summary']
    steepness = extras['steepness']['summary']
    suitability = extras['suitability']['summary']
    connectivity = segments['steps']
    
    
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
        print('distance = {}'.format(distance))
        
    try:
        duration != 0
    except LookupError as e:
        print(e)
    else:
        print('duration = {}'.format(duration))
        
        
    try:
        surface_type != 0
    except LookupError as e:
        print(e)
    else:
        wt_surface_type_avg = weighted_avgfunc(surface_type)
        print('weighted average surface type ={}'.format(wt_surface_type_avg))
        
        
    try:
        waycategory != 0
    except LookupError as e:
        print(e)
    else:
        wt_category_avg = weighted_avgfunc(waycategory)
        print('weighted average road category = {}'.format(wt_category_avg))
        
    try:
        waytypes != 0
    except LookupError as e:
        print(e)
    else:
        wt_waytypes_avg = weighted_avgfunc(waytypes)
        print('weighted average waytype = {}'.format(wt_waytypes_avg))
        
    try:
        steepness != 0
    except LookupError as e:
        print(e)
    else:
        wt_steep_avg = weighted_avgfunc(steepness)
        print('weighted average steepness = {}'.format(wt_steep_avg))
        
    try:
        suitability != 0
    except LookupError as e:
        print(e)
    else:
        wt_suitability_avg = weighted_avgfunc(suitability)
        print('weighted average suitability = {}'.format(wt_suitability_avg))
        
    try:
        connectivity != 0
        #print('route connections = {}'.format(len(connectivity)))
    except LookupError as e:
        print(e)
    else:
        print('street connections = {}'.format(len(connectivity)))
    

   
    
    







#function tested with second point
stuttgart_airport =[[9.19515,48.690494],[7.850182, 47.99501]]
points = [[7.854559, 48.003247],[7.850182, 47.99501]]
ors_key = '5b3ce3597851110001cf6248480fc21010a54f35ad5e49b6d97490fb'
dat_extract(points,ors_key)