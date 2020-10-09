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


def bikeability(place, scale = 'city',data = False):
    ''' A function that would calculate bikeability value for a given
    place of interest. 

    Parameters
    place: the place of interest e.g "Freiburg, Germany" datatype = string
    Scale: can be either "grid" or "city" default is "city" datatype = string
    data: if True output returns a dataframe along with the standard dictionary 
    output, datatype = boolean

    Returns the average_index for bikeability(number between 0 and 100) and some
    summary statistics of index, datatype = dictionary or dataframe and dictionary
    if data is set as True.
    
    Usage example
    a = bikeability('Freiburg, Germany', scale ='grid', data = False) ... for grid scale approach
    a,b = bikeability('Freiburg, Germany', scale ='grid', data = True)
    a =bikeability('Freiburg, Germany', scale = 'city')... for city scale approach
    a,b =bikeability('Freiburg, Germany', scale = 'city', data = True)
    '''

    if scale != 'grid':

        place = place

        # Create and set osmnx to select important tags
        useful_tags_path = ['bridge', 'length', 'oneway', 'lanes', 'ref', 'name',
                            'highway', 'maxspeed', 'service', 'access', 'area', 'cycleway',
                            'landuse', 'width', 'est_width', 'junction', 'surface']
        ox.utils.config(useful_tags_path=useful_tags_path)

        # Create basic city graph
        place_name = place
        graph = ox.graph_from_place(place_name, network_type='bike', retain_all=True)

        # # Calculate and add edge closeness centrality(connectedness)
        centrality = nx.degree_centrality(nx.line_graph(graph))
        nx.set_edge_attributes(graph, centrality, 'centrality')

        # Extract nodes and edges to geopandas from graph
        edges = ox.graph_to_gdfs(graph, nodes=False)

        # Remove unwanted columns and add weight variable
        cols = (['highway', 'cycleway', 'surface', 'maxspeed', 'length', 'lanes', 'oneway',
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
        df['cycleway'] = df['cycleway'].astype(str)

        # Dataframe cleaning and preprocessing
        # highway column
        df['highway'] = df['highway'].str.replace(r'[^\w\s-]', '')
        highway_cols = (pd.DataFrame(df.highway.str.split(' ', expand=True)))
        highway_map = ({'service': 6, 'None': np.nan, 'residential': 8, 'unclassified': 7, 'footway': 7, 'track': 5,
                        'tertiary': 6, 'living_street': 9, 'path': 5, 'pedestrian': 7, 'secondary': 5,
                        'primary': 2, 'steps': 2, 'cycleway': 10, 'rest_area': 5, 'primary_link': 2, 'ferry': 1,
                        'construction': 2, 'byway': 8, 'bridleway': 6, 'trunk': 2, 'trunk_link': 2, 'motorway': 1, 'motorway_link': 1})
        for column in highway_cols:
            highway_cols[column] = highway_cols[column].map(highway_map)
        highway_cols['mean'] = np.nanmean(highway_cols, axis=1)
        df['highway'] = round(highway_cols['mean'])

        # cycleway column
        df['cycleway'] = df['cycleway'].str.replace(r'[^\w\s-]', '')
        cycleway_cols = (pd.DataFrame(df.cycleway.str.split(' ', expand=True)))
        cycleway_map = ({'opposite': 9, 'lane': 9, 'share_busway': 8, 'shared_lane': 8, 'segregated': 10,
                        'no': 1, 'opposite_lane': 9, 'crossing': 10, 'track': 10, 'designated': 10,
                        'opposite_share_busway': 8, 'seperate': 10, 'shoulder': 8})
        for column in cycleway_cols:
            cycleway_cols[column] = cycleway_cols[column].map(cycleway_map)
        cycleway_cols['mean'] = np.nanmean(cycleway_cols, axis=1)
        df['cycleway'] = round(cycleway_cols['mean'])

        # surface column
        df['surface'] = df['surface'].str.replace(r'[^\w\s-]', '')
        surface_cols = (pd.DataFrame(df.surface.str.split(' ', expand=True)))
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
        oneway_map = {0: 5, 1: 10, -1: 5}
        df['oneway'] = df['oneway'].map(oneway_map)

        # width column
        df.loc[df['width'] < 2, 'width'] = 1
        df.loc[df['width'] > 6, 'width'] = 6
        df['width'] = round(df['width'])
        width_map = ({1: 1, 2: 2, 3: 5, 4: 7, 5: 9, 6: 10})
        df['width'] = df['width'].map(width_map)

        # normalize centrality column (between o and 10)
        df['centrality'] = ((df['centrality'] - np.min(df['centrality'])) /
                            (np.max(df['centrality']) - np.min(df['centrality']))) * 10

        # Switch to new df for calculation
        d_frame = df.copy(deep=True)

        # Multiply variables by weights
        d_frame['cycleway'] = d_frame['cycleway'] * 0.208074534
        d_frame['surface'] = d_frame['surface'] * 0.108695652
        d_frame['highway'] = d_frame['highway'] * 0.167701863
        d_frame['maxspeed'] = d_frame['maxspeed'] * 0.189440994
        d_frame['lanes'] = d_frame['lanes'] * 0.108695652
        d_frame['centrality'] = d_frame['centrality'] * 0.071428571
        d_frame['width'] = d_frame['width'] * 0.086956522
        d_frame['oneway'] = d_frame['oneway'] * 0.059006211

        # Normalize variables between 0 and 1
        d_frame['index'] = (np.nanmean(d_frame[['cycleway', 'highway', 'surface', 'maxspeed', 'lanes', 'width', 'oneway',
                                                'centrality']], axis=1, dtype='float64')) * 80
        
        # Final statistics index of city
        mean_index = np.average(d_frame['index'], weights=d_frame['length'])
        max_index = d_frame['index'].max()
        min_index = d_frame['index'].min()
        std_index = d_frame['index'].std()

        # Plot result
        #d_frame.plot(column = 'index',legend = True)

        # Result dictionary
        result = ({'place': place, 'average_index': mean_index, 'max_index': max_index,
                'min_index': min_index, 'std_index': std_index})
        

    else:
        #Get bounding box for place
        place_name = place
        area = ox.gdf_from_place(place_name)
        xmin,ymin,xmax,ymax = area.total_bounds

        #divide into grids x = lon, y = lat 
        height = 0.041667
        width = 0.041667
        rows = int(np.ceil((ymax-ymin) /  height))
        cols = int(np.ceil((xmax-xmin) / width))
        XleftOrigin = xmin
        XrightOrigin = xmin + width
        YtopOrigin = ymax
        YbottomOrigin = ymax- height
        polygons = []
        for i in range(cols):
            Ytop = YtopOrigin
            Ybottom =YbottomOrigin
            for j in range(rows):
                polygons.append(Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)])) 
                Ytop = Ytop - height
                Ybottom = Ybottom - height
            XleftOrigin = XleftOrigin + width
            XrightOrigin = XrightOrigin + width

        #Ensure the grids are within the polygon
        grid_list = []
        for i in range(len(polygons)):
            p = Point(polygons[i].centroid.x, polygons[i].centroid.y)
            geome = shape(polygons[i])
            q =gpd.GeoDataFrame({'geometry':geome}, index=[0])
            if area.geometry.iloc[0].contains(polygons[i])== True:
                grid_list.append(q)
            #elif p.within(area.geometry.iloc[0]) == True and area.geometry.iloc[0].contains(polygons[i])== False:
            elif area.geometry.iloc[0].intersects(polygons[i]):
                #grid_list.append(polygons[i])
                clip = gpd.clip(area, q)
                grid_list.append(clip)
            

        #Initialize important variables
        dflist = []
        exception_grids = []
        dfs = []

        for i in tqdm(range(len(grid_list))):
        
            #graph
            useful_tags_path = ['bridge', 'length', 'oneway', 'lanes', 'ref',
            'name', 'highway', 'maxspeed', 'surface', 'area', 
            'landuse', 'width', 'est_width', 'junction','cycleway']                 
            ox.utils.config(useful_tags_path=useful_tags_path)
            
            try:
                #cf = '["access"!~"private|no"]' , custom_filter=cf
                box_graph =ox.graph_from_polygon(grid_list[i].geometry.iloc[0], network_type='bike',retain_all=True)
                pass
            except Exception as e:
                print('{} at grid {}, skip grid'.format(e, i+1)) 
                exception_grids.append(i+1) 
                continue    

            # Calculate and add edge closeness centrality(connectedness)
            centrality = nx.degree_centrality(nx.line_graph(box_graph))
            nx.set_edge_attributes(box_graph, centrality, 'centrality')

            # Extract nodes and edges to geopandas from graph
            edges = ox.graph_to_gdfs(box_graph, nodes= False)
            
            # Select only the important variables
            cols = (['highway','cycleway', 'surface', 'maxspeed', 'length', 'lanes', 'oneway',
                    'width', 'centrality', 'geometry'])
            try:
                df = edges[cols]
                pass
            except KeyError as e:
                print('{} at grid {}, skip grid'.format(e, i+1)) 
                exception_grids.append(i+1) 
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
            cycleway_map = ({'opposite':9, 'lane':9, 'share_busway':8, 'shared_lane':8,'segregated':10,
                            'no':1, 'opposite_lane':9, 'crossing':10, 'track':10, 'designated':10,
                            'opposite_share_busway':8, 'seperate':10, 'shoulder':8})
            for column in cycleway_cols:
                cycleway_cols[column] = cycleway_cols[column].map(cycleway_map)
            cycleway_cols['mean'] = np.nanmean(cycleway_cols, axis=1)
            df['cycleway'] = round(cycleway_cols['mean'])

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
            oneway_map = {0: 5, 1: 10, -1:5}
            df['oneway'] = df['oneway'].map(oneway_map)

            # width column
            df.loc[df['width'] < 2, 'width'] = 1
            df.loc[df['width'] > 6, 'width'] = 6
            df['width'] = round(df['width'])
            width_map = ({1: 1, 2: 2, 3: 5, 4: 7, 5: 9, 6: 10})
            df['width'] = df['width'].map(width_map)

            # normalize centrality column (between o and 10)
            df['centrality'] =((df['centrality'] - np.min(df['centrality'])) / (np.max(df['centrality']) - np.min(df['centrality']))) * 10
        
            #Switch to new df for calculation
            d_frame = df.copy(deep =True)

            # Multiply variables by weights
            d_frame['cycleway'] = d_frame['cycleway'] * 0.208074534
            d_frame['surface'] = d_frame['surface'] * 0.108695652
            d_frame['highway'] = d_frame['highway'] * 0.167701863
            d_frame['maxspeed'] = d_frame['maxspeed'] * 0.189440994
            d_frame['lanes'] = d_frame['lanes'] * 0.108695652
            d_frame['centrality'] = d_frame['centrality'] * 0.071428571
            d_frame['width'] = d_frame['width'] * 0.086956522
            d_frame['oneway'] = d_frame['oneway'] * 0.059006211
        
            d_frame['index'] = (np.nanmean(d_frame[['cycleway','highway', 'surface', 'maxspeed', 'lanes', 'width', 'oneway',
                                                'centrality']], axis=1,dtype='float64')) * 80
            
            d_frame['grid_index'] =  np.average(d_frame['index'],weights=d_frame['length'])
            dflist.append(d_frame)
            dfs.append(df)
            
        #Final statistics index of city in dictionary
        df_indexes = pd.concat(dflist)
        result = ({'place':place_name,
        'average_index':np.average(df_indexes['index'],weights=df_indexes['length']),
        'max_index':df_indexes['index'].max(), 
        'min_index':df_indexes['index'].min(),
        'std_index':df_indexes['index'].std(),
        'grids':len(grid_list),
        'nsegments':len(df_indexes),
        'unused_grids':len(exception_grids)})
    
    if data == False:
        return(result)
    else:
        return(d_frame, result)
    

        



        


    
