import openrouteservice
from openrouteservice import convert
import json

#Get ORS route as geojson file
start = [7.854559, 48.003247]
end = [7.850182, 47.99501]

api_key = '5b3ce3597851110001cf6248480fc21010a54f35ad5e49b6d97490fb'
coords = (start, end)

client = openrouteservice.Client(key=api_key) # Specify your personal API key

geometry = client.directions(
    coords, 
    format='geojson', 
    profile='cycling-regular', 
    instructions=True, 
    instructions_format='text',
    attributes=['avgspeed', 'detourfactor', 'percentage'], 
    # elevation=True, messes with the coordinates 
    maneuvers=True,
    preference="recommended",
    extra_info=["steepness", "suitability", "surface", "waycategory", "waytype", "tollways", "traildifficulty"]
    )

with open('ors_route.geojson', 'w') as f:
   json.dump(geometry, f)

propties = (geometry['features'][0]['properties'])
type(propties)
propties.keys()

#from summary
distance =propties['summary']['distance']
print('distance = {}'.format(distance))
duration =propties['summary']['duration']
print('duration = {}'.format(duration))
#waypoints are list items
waypoints = (propties['way_points'])
print('waypoints ')
print(*waypoints, sep = "\n") 

#from extras
extras =propties['extras']
extras.keys()

surface_type = extras['surface']['summary']
print('surface_types')
print(*surface_type,sep = '\n')
waycategory = extras['waycategory']['summary']
print('waycategories')
print(*waycategory, sep = '\n')
waytypes = extras['waytypes']['summary']
print('waytypes')
print(*waytypes, sep = '\n')
steepness = extras['steepness']['summary']
print('steepness')
print(*steepness, sep = '\n')
suitability = extras['suitability']['summary']
print(suitability)
print(*suitability, sep = '\n')

#from segments
propties['segments'][0].keys()
steps = propties['segments'][0]
connectivity = propties['segments'][0]['steps']
print(len(connectivity))

#To search for street turns
instructions = []
for x in range(len(connectivity)):
    #print(connectivity[x]['instruction'])
    ins = connectivity[x]['instruction']
    instructions.append(ins)
subs = 'onto'
connections = [i for i in instructions if subs in i]
streets =[i.partition(subs)[2] for i in connections]
print(streets)

#Average values for factors
import numpy as np
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
    
            
weighted_avgfunc(surface_type)
weighted_avgfunc(waycategory)
weighted_avgfunc(waytypes)
weighted_avgfunc(steepness)
weighted_avgfunc(suitability)