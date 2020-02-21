from osmnxdata_mined import geodf as test, frb
import re
import pandas as pd
import geopandas as gpd
from shapely import wkt
from orsdata_explore import connectivity, distance as tot_dist
import numpy as np

#choose vars of interest for wrangling
joined = test[['oneway', 'lanes', 'name','highway','maxspeed',
        'length', 'bridge','width', 'access', 'service', 'tunnel',
        'geometry']]

#Change dataframe dtype to string for wrangling
joined =joined.astype(str)

#Convert the boolean to 1 and o
joined['oneway'] =joined.oneway.str.replace('True','1')
joined['oneway'] =joined.oneway.str.replace('False','0')

#Remove multiple entries in one series/column
joined['name'] =joined.name.str.split(',').apply(lambda x: x[0])
joined['name'] = joined.name.str.replace(r'[^\w\s-]','')

joined['lanes'] =joined.lanes.str.split(',').apply(lambda x: x[0])
joined['lanes'] = joined.lanes.str.replace(r'[^\w\s-]','')

joined['highway'] = joined.highway.str.split(',').apply(lambda x: x[0])
joined['highway'] = joined.highway.str.replace(r'[^\w\s-]','')

joined['maxspeed'] =joined.maxspeed.str.split(',').apply(lambda x: x[0])
joined['maxspeed'] =joined.maxspeed.str.replace(r'[^\w\s-]','')

#convert datatypes to useful forms
joined['oneway'] = pd.to_numeric(joined.oneway,errors='coerce', downcast='integer')
joined['maxspeed'] = pd.to_numeric(joined.maxspeed,errors='coerce', downcast='integer')
joined['lanes'] =pd.to_numeric(joined.lanes,errors='coerce', downcast='integer')
joined['geometry'] = joined['geometry'].apply(wkt.loads)
joined = gpd.GeoDataFrame(joined, geometry='geometry',crs={'init':'epsg:4326'})
###############

#create weighting df for summarizing route into a row
name = []
dist = []
weight = []
for x in range(len(connectivity)):
    if connectivity[x]['name'] != '-':
        name.append(connectivity[x]['name'])
        dist.append(connectivity[x]['distance'])
        weight.append(connectivity[x]['distance']/tot_dist)
  
df = pd.DataFrame(list(zip(name, dist, weight)), 
               columns =['name', 'distance','weight']) 
df['name'] =df.name.str.split(',').apply(lambda x: x[0])
df.dtypes  

mergedwt =joined.merge(df, on='name') #merging selected only the streets in ors_route

# summarize mean
gouped_nm =mergedwt.groupby('name', as_index=False)['maxspeed',
'lanes','oneway','distance','weight'].mean()

#weighted mean excluding nan / function
def weighted_mean(arr_lst,wt_lst):
    indices = ~np.isnan(arr_lst)
    avg_wt = np.average(arr_lst[indices],weights=wt_lst[indices])
    return avg_wt

avg_maxspeed =weighted_mean(mergedwt['maxspeed'],mergedwt['weight'])
avg_lanes = round(weighted_mean(mergedwt.lanes,mergedwt.weight)) #to nearest whole no
avg_oneway = round(weighted_mean(mergedwt.oneway,mergedwt.weight)) #true or false. o mean false
##################
