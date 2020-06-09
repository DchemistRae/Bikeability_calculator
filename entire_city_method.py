from sklearn import preprocessing
import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import pandas as pd
import numpy as np
import networkx as nx
from os import path

place = 'Berlin, Germany'
#place = "Emmendingen, Germany"

# Create and set osmnx to select important tags
useful_tags_path = ['bridge', 'tunnel', 'oneway', 'lanes', 'ref', 'name',
                    'highway', 'maxspeed', 'service', 'access', 'area',
                    'landuse', 'width', 'est_width', 'junction', 'surface']
ox.utils.config(useful_tags_path=useful_tags_path)

# Create basic city graph
place_name = place
graph = ox.graph_from_place(place_name, network_type='bike',retain_all=True)

# Plot graph of place
#fig, ax = ox.plot_graph(graph)
# plt.tight_layout()

# Calculate edge degree centrality(connectedness)
centrality = nx.degree_centrality(nx.line_graph(graph))
# add to edge attribute
nx.set_edge_attributes(graph, centrality, 'centrality')

# Extract nodes and edges to geopandas from graph
edges = ox.graph_to_gdfs(graph, nodes= False)

# Remove unwanted columns and add weight variable
edges['weight'] = edges.geometry.length
cols = (['highway', 'surface', 'maxspeed', 'weight', 'lanes', 'oneway',
         'width', 'centrality', 'geometry'])
df = edges[cols]

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

# Dataframe cleaning and preprocessing
# highway column
df['highway'] = df['highway'].str.replace(r'[^\w\s-]', '')
highway_cols = (pd.DataFrame(df.highway.str.split(' ', expand = True)))
highway_map = ({'service': 6, 'None': np.nan, 'residential': 8, 'unclassified': 7, 'footway': 7, 'track': 5,
                'tertiary': 6, 'living_street': 9, 'path': 5, 'pedestrian': 7, 'secondary': 5,
                'primary': 2, 'steps': 2, 'cycleway': 10, 'rest_area': 5, 'primary_link': 2, 'ferry': 1,
                'construction': 2, 'byway': 8, 'bridleway': 6, 'trunk': 2, 'trunk_link': 2, 'motorway': 1, 'motorway_link': 1})
for column in highway_cols:
    highway_cols[column] = highway_cols[column].map(highway_map)
highway_cols['mean'] = np.nanmean(highway_cols, axis=1)
df['highway'] = round(highway_cols['mean'])

# surface column
df['surface'] = df['surface'].str.replace(r'[^\w\s-]', '')
surface_cols = (pd.DataFrame(df.surface.str.split(' ', expand = True)))
surface_map = ({'asphalt': 10, 'paved': 10, 'cobblestone': 5, 'fine_gravel': 9,
                'ground': 7, 'sett': 6, 'gravel': 7, 'metal': 6, 'compacted': 10,
                'dirt': 6, 'paving_stones': 7, 'grass_paver': 5, 'unpaved': 8,
                'pebblestone': 9, 'concrete': 10, 'grass': 5, 'mud': 1})
for column in surface_cols:
    surface_cols[column] = surface_cols[column].map(surface_map)
surface_cols['mean'] = np.nanmean(surface_cols, axis=1)
df['surface'] = round(surface_cols['mean'])

# maxspeed column
df.loc[df['maxspeed'] > 110, 'maxspeed'] = 110
df.loc[df['maxspeed'] < 20, 'maxspeed'] = 20
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
x = df[['centrality']].values.astype(float)
min_max_scaler = preprocessing.MinMaxScaler()
df['centrality_scaled'] = min_max_scaler.fit_transform(x)
df['centrality_scaled'] = df['centrality_scaled'] * 10

# Index calculation
d_frame = df.copy()

d_frame['surface'] = d_frame['surface'] * 0.140562249
d_frame['highway'] = d_frame['highway'] * 0.269076305
d_frame['maxspeed'] = d_frame['maxspeed'] * 0.24497992
d_frame['lanes'] = d_frame['lanes'] * 0.140562249
d_frame['centrality_scaled'] = d_frame['centrality_scaled'] * 0.092369478
d_frame['width'] = d_frame['width'] * 0.112449799
# centrality and oneway droped before calculating index
#d_frame.drop(['centrality','oneway'], axis=1, inplace=True)
# sum of weighted variables from row index 3 >>>>always
# check for correctness
d_frame['summation'] = (d_frame.loc[:, ['highway', 'surface',
                                        'maxspeed', 'lanes', 'width',
                                        'centrality_scaled']].sum(axis=1))
# Get a value between 0 and 100 for bikeability index (maximum weight is 60)
d_frame['index'] = ((d_frame['summation'] * 100) / 10)
# Final statistics index of city
mean_index = np.average(d_frame['index'],weights=d_frame['weight'])
max_index = d_frame['index'].max()
min_index = d_frame['index'].min()

# Plot result
#d_frame.plot(column = 'index',legend = True)

#Result dictionary
result = ({'place':place,'average_index':mean_index, 'max_index':max_index,'min_index':min_index})

#Save to file
if path.exists("result_cities.csv"):
    result_df = pd.read_csv('result_cities.csv')
    result_df = result_df.append(result, ignore_index=True)
    result_df.to_csv('result_cities.csv',index = False)
else:
    result_df = pd.DataFrame(columns= ('place','average_index','max_index','min_index'))
    result_df = result_df.append(result, ignore_index=True)
    result_df.to_csv('result_cities.csv',index = False)



###########
#dna = d_frame.dropna()
#np.average(dna['index'],weights=dna['weight'])
