import osmnx as ox 
import networkx as nx 
import pandas as pd 
import geopandas as gpd
import numpy as np 
from shapely.geometry import shape, Polygon, Point
import requests
import geojson
from tqdm import tqdm
from os import path

#Get bounding box for place
place_name = 'Bremen, Germany'
area = ox.gdf_from_place(place_name)
xmin,ymin,xmax,ymax = area.total_bounds

#divide into grids x = lon, y = lat and ensure point within geometry
cols = np.linspace(ymin, ymax, num=6)
rows = np.linspace(xmin, xmax, num=6)

cell_centers = []
for x in rows:
    for y in cols:
        p =Point(x,y)
        if p.within(area.geometry.iloc[0]) == True:
            cell_centers.append([x,y])

#Initialize important variables
dflist = []
exception_counts = []

for i in tqdm(range(len(cell_centers))):
    #Retrieve isochrones for center geometries of grids (change index)
    body = {"locations":[cell_centers[i]],"range":[720],"attributes":["area","reachfactor","total_pop"],"intersections":"true","interval":720,"location_type":"start","range_type":"time","area_units":"m","units":"m"}
    #print('step {} of {}'.format(i+1, len(cell_centers)))
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': '5b3ce3597851110001cf6248480fc21010a54f35ad5e49b6d97490fb',
        'Content-Type': 'application/json; charset=utf-8'
    }
    call = requests.post('https://api.openrouteservice.org/v2/isochrones/cycling-regular', json=body, headers=headers)

    #print(call.status_code, call.reason)
    #print(call.text)
    try:
        output = call.json()
        polys = output['features'][0]['geometry']
        pass
    except KeyError as e:
        print('{} at grid {}, skip grid'.format(e, i+1))
        exception_counts.append(i+1) 
        continue 
    except Exception as e:
        print('{} at grid {}, skip grid'.format(e, i+1))
        exception_counts.append(i+1) 
        continue  
    
    total_pop =output['features'][0]['properties']['total_pop']
    size = (output['features'][0]['properties']['area'])/1e+6
    pop_density = total_pop/size #per km^2
    if pop_density <= 100:
        print('low population density at grid{}'.format(i+1))
        exception_counts.append(i+1)
        continue 
    geom = shape(polys)
    b =gpd.GeoDataFrame({'geometry':geom}, index=[0]) #polygon object returned


    #graph
    useful_tags_path = ['bridge', 'tunnel', 'oneway', 'lanes', 'ref',
    'name', 'highway', 'maxspeed', 'surface', 'area', 
    'landuse', 'width', 'est_width', 'junction','cycleway']                 
    ox.utils.config(useful_tags_path=useful_tags_path)
    box_graph =ox.graph_from_polygon(b.geometry.iloc[0], network_type='bike',retain_all=True)

    # Plot graph of place
    #fig, ax = ox.plot_graph(box_graph)

    # Calculate edge closeness centrality(connectedness)
    centrality = nx.degree_centrality(nx.line_graph(box_graph))
    # add to edge attribute
    nx.set_edge_attributes(box_graph, centrality, 'centrality')

    # Extract nodes and edges to geopandas from graph
    edges = ox.graph_to_gdfs(box_graph, nodes= False)

    # Remove unwanted columns and add weight variable
    edges['weight'] = edges.geometry.length
    cols = (['highway','cycleway', 'surface', 'maxspeed', 'weight', 'lanes', 'oneway',
            'width', 'centrality', 'geometry'])
    try:
        df = edges[cols]
        pass
    except KeyError as e:
        print('{} at grid {}, skip grid'.format(e, i+1)) 
        exception_counts.append(i+1) 
        continue      
            
    # Set appropriate data types
    df['maxspeed'] = pd.to_numeric(
        df['maxspeed'], errors='coerce', downcast='integer')
    df['lanes'] = pd.to_numeric(
        df['lanes'], errors='coerce', downcast='integer')
    df['width'] = pd.to_numeric(
        df['width'], errors='coerce', downcast='unsigned')
    df['highway'] = df['highway'].astype(str)
    df['surface'] = df['surface'].astype(str)
    df['oneway'] = df['oneway'].astype(int)
    df['cycleway'] = df['cycleway'].astype(str)

    # Dataframe cleaning and preprocessing
    # highway column
    df['highway'] = df['highway'].str.replace(r'[^\w\s-]', '')
    highway_cols = (pd.DataFrame(df.highway.str.split(' ', expand = True)))
    highway_map = ({'service': 6, 'None': np.nan, 'residential': 8, 'unclassified': 7, 'footway': 7, 'track': 5, 'tertiary_link':6,
                    'tertiary': 6, 'living_street': 9, 'path': 5, 'pedestrian': 7, 'secondary': 5, 'secondary_link':5,
                    'primary': 2, 'steps': 2, 'cycleway': 10, 'rest_area': 5, 'primary_link': 2, 'ferry': 1,
                    'construction': 2, 'byway': 8, 'bridleway': 6, 'trunk': 2, 'trunk_link': 2, 'motorway': 1, 'motorway_link': 1})
    for column in highway_cols:
        highway_cols[column] = highway_cols[column].map(highway_map)
    highway_cols['mean'] = np.nanmean(highway_cols, axis=1)
    df['highway'] = round(highway_cols['mean'])

    #cycleway column
    df['cycleway'] = df['cycleway'].str.replace(r'[^\w\s-]', '')
    cycleway_cols = (pd.DataFrame(df.cycleway.str.split(' ', expand = True)))
    cycleway_map = ({'opposite':9, 'lane':9, 'share_busway':8, 'shared_lane':8,
                    'no':1, 'opposite_lane':9, 'crossing':10, 'track':10, 'designated':10,
                    'opposite_share_busway':8, 'seperate':10, 'shoulder':8})
    for column in cycleway_cols:
        cycleway_cols[column] = cycleway_cols[column].map(cycleway_map)
    cycleway_cols['mean'] = np.nanmean(cycleway_cols, axis=1)
    df['cycleway'] = round(cycleway_cols['mean'])
    df['cycleway'] =df['cycleway'].fillna(df['highway']) #replace na with highway vlues

    # surface column
    df['surface'] = df['surface'].str.replace(r'[^\w\s-]', '')
    surface_cols = (pd.DataFrame(df.surface.str.split(' ', expand = True)))
    surface_map = ({'asphalt': 10, 'paved': 10, 'cobblestone': 3, 'fine_gravel': 9,
                    'ground': 6, 'sett': 4, 'gravel': 7, 'metal': 7, 'compacted': 9,
                    'dirt': 6, 'paving_stones': 7, 'grass_paver': 4, 'unpaved': 7,
                    'pebblestone': 7, 'concrete': 10, 'grass': 5, 'mud': 2,'sand':5,
                    'wood':4, 'earth':6, 'woodchips':3, 'snow':2, 'ice':2, 'salt':2})
    for column in surface_cols:
        surface_cols[column] = surface_cols[column].map(surface_map)
    surface_cols['mean'] = np.nanmean(surface_cols, axis=1)
    df['surface'] = round(surface_cols['mean'])

    # maxspeed column
    df.loc[df['maxspeed'] > 110, 'maxspeed'] = 110
    df.loc[df['maxspeed'] < 20, 'maxspeed'] = 20
    df['maxspeed'] = round(df['maxspeed'], -1)
    maxspeed_map = ({20: 10, 30: 9, 40: 8, 50: 7, 60: 6,
                    70: 5, 80: 4, 90: 3, 100: 2, 110: 1})
    df['maxspeed'] = df['maxspeed'].map(maxspeed_map)

    # lanes column
    df.loc[df['lanes'] > 8, 'lanes'] = 8
    lanes_map = {1: 10, 2: 9, 3: 5, 4: 5, 5: 3, 6: 3, 7: 2, 8: 1}
    df['lanes'] = df['lanes'].map(lanes_map)

    # oneway column
    oneway_map = {0: 5, 1: 10}
    df['oneway'] = df['oneway'].map(oneway_map)

    # width column
    df.loc[df['width'] < 2, 'width'] = 1
    df.loc[df['width'] > 6, 'width'] = 6
    df['width'] = round(df['width'])
    width_map = ({1: 1, 2: 2, 3: 5, 4: 7, 5: 9, 6: 10})
    df['width'] = df['width'].map(width_map)

    # normalize centrality column
    df['centrality_scaled'] =(df['centrality'] - np.min(df['centrality'])) / (np.max(df['centrality']) - np.min(df['centrality']))
    df['centrality_scaled'] = df['centrality_scaled'] * 10

    # Index calculation
    
    d_frame = df.copy()

    d_frame['cycleway'] = d_frame['cycleway'] * 0.269076305
    d_frame['surface'] = d_frame['surface'] * 0.140562249
    d_frame['highway'] = d_frame['highway'] * 0.269076305
    d_frame['maxspeed'] = d_frame['maxspeed'] * 0.24497992
    d_frame['lanes'] = d_frame['lanes'] * 0.140562249
    d_frame['centrality_scaled'] = d_frame['centrality_scaled'] * 0.092369478
    d_frame['width'] = d_frame['width'] * 0.112449799

    #sum important columns
    d_frame['summation'] = (d_frame.loc[:, ['cycleway', 'surface',
                                            'maxspeed', 'lanes', 'width',
                                            'centrality_scaled']].sum(axis=1))

    # Get a value between 0 and 100 for bikeability index (maximum weight is 60)
    d_frame['index'] = ((d_frame['summation'] * 100) / 10)
    dflist.append(d_frame)
    
#Final statistics index of city in dictionary
df_indexes = pd.concat(dflist)
results = ({'place':place_name,
'average_index':np.average(df_indexes['index'],weights=df_indexes['weight']),
'max_index':df_indexes['index'].max(), 
'min_index':df_indexes['index'].min(),
'std_index':df_indexes['index'].std(),
'grids':len(cell_centers),
'nsegments':len(df_indexes),
'unused_grids':len(exception_counts)})

# Plot result
#plot = d_frame.plot(column = 'index',legend = True)

#Save to file
if path.exists("result_grid.csv"):
    result_d = pd.read_csv('result_grid.csv')
    result_d = result_d.append(results, ignore_index=True)
    result_d.to_csv('result_grid.csv',index = False)
else:
    result_d = pd.DataFrame(columns= ('place','average_index','max_index','min_index','std_index'))
    result_d = result_d.append(results, ignore_index=True)
    result_d.to_csv('result_grid.csv',index = False)

#Save dataframe to file as well 
#df_indexes.to_csv('index_data\{}_index.csv'.format(place_name.split(',')[0]))
  



