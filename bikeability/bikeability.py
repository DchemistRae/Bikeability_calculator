import osmnx as ox
import networkx as nx
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import shape, Polygon, Point
import warnings
import numpy as np

warnings.filterwarnings(action='ignore', message='Mean of empty slice')

def _prepare_graph(place, useful_tags_way, network_type, polygon=None):
    """Create a networkx graph for the specified place or polygon."""
    ox.utils.config(useful_tags_way=useful_tags_way)
    if polygon is not None:
        return ox.graph_from_polygon(polygon, network_type=network_type, retain_all=True)
    return ox.graph_from_place(place, network_type=network_type, retain_all=True)

def _add_centrality(graph):
    """Add degree centrality to edges as an attribute."""
    centrality = nx.degree_centrality(nx.line_graph(graph))
    nx.set_edge_attributes(graph, centrality, 'centrality')

def _extract_edges(graph):
    """Extract edges as a GeoDataFrame."""
    return ox.graph_to_gdfs(graph, nodes=False)

def _clean_and_map_columns(df, context='city'):
    """Clean and map columns for scoring."""
    # Highway
    df['highway'] = df['highway'].str.replace(r'[^\w\s-]', '', regex=True)
    highway_cols = pd.DataFrame(df.highway.str.split(' ', expand=True))
    highway_map = (
        {'service': 6, 'None': np.nan, 'residential': 8, 'unclassified': 7, 'footway': 7, 'track': 5,
         'tertiary': 6, 'living_street': 9, 'path': 5, 'pedestrian': 7, 'secondary': 5,
         'primary': 2, 'steps': 2, 'cycleway': 10, 'rest_area': 5, 'primary_link': 2, 'ferry': 1,
         'construction': 2, 'byway': 8, 'bridleway': 6, 'trunk': 2, 'trunk_link': 2, 'motorway': 1, 'motorway_link': 1}
        if context == 'city' else
        {'service': 6, 'None': np.nan, 'residential': 8, 'unclassified': 7, 'footway': 7, 'track': 5, 'tertiary_link': 6,
         'tertiary': 6, 'living_street': 9, 'path': 5, 'pedestrian': 7, 'secondary': 5, 'secondary_link': 5,
         'primary': 2, 'steps': 2, 'cycleway': 10, 'rest_area': 5, 'primary_link': 2, 'ferry': 1,
         'construction': 2, 'byway': 8, 'bridleway': 6, 'trunk': 2, 'trunk_link': 2, 'motorway': 1, 'motorway_link': 1}
    )
    for column in highway_cols:
        highway_cols[column] = highway_cols[column].map(highway_map)
    highway_cols['mean'] = np.nanmean(highway_cols, axis=1)
    df['highway'] = round(highway_cols['mean'])

    # Cycleway
    df['cycleway'] = df['cycleway'].str.replace(r'[^\w\s-]', '', regex=True)
    cycleway_cols = pd.DataFrame(df.cycleway.str.split(' ', expand=True))
    cycleway_map = {'opposite': 9, 'lane': 9, 'share_busway': 8, 'shared_lane': 8, 'segregated': 10,
                    'no': 1, 'opposite_lane': 9, 'crossing': 10, 'track': 10, 'designated': 10,
                    'opposite_share_busway': 8, 'seperate': 10, 'shoulder': 8}
    for column in cycleway_cols:
        cycleway_cols[column] = cycleway_cols[column].map(cycleway_map)
    cycleway_cols['mean'] = np.nanmean(cycleway_cols, axis=1)
    df['cycleway'] = round(cycleway_cols['mean'])

    # Surface
    df['surface'] = df['surface'].str.replace(r'[^\w\s-]', '', regex=True)
    surface_cols = pd.DataFrame(df.surface.str.split(' ', expand=True))
    surface_map = (
        {'asphalt': 10, 'paved': 10, 'cobblestone': 5, 'fine_gravel': 9,
         'ground': 7, 'sett': 6, 'gravel': 7, 'metal': 6, 'compacted': 10,
         'dirt': 6, 'paving_stones': 7, 'grass_paver': 5, 'unpaved': 8,
         'pebblestone': 9, 'concrete': 10, 'grass': 5, 'mud': 1}
        if context == 'city' else
        {'asphalt': 10, 'paved': 10, 'cobblestone': 3, 'fine_gravel': 9,
         'ground': 6, 'sett': 4, 'gravel': 7, 'metal': 7, 'compacted': 9,
         'dirt': 6, 'paving_stones': 7, 'grass_paver': 4, 'unpaved': 7,
         'pebblestone': 7, 'concrete': 10, 'grass': 5, 'mud': 2, 'sand': 5,
         'wood': 4, 'earth': 6, 'woodchips': 3, 'snow': 2, 'ice': 2, 'salt': 2}
    )
    for column in surface_cols:
        surface_cols[column] = surface_cols[column].map(surface_map)
    surface_cols['mean'] = np.nanmean(surface_cols, axis=1)
    df['surface'] = round(surface_cols['mean'])

    # Maxspeed
    df.loc[df['maxspeed'] > 110, 'maxspeed'] = 110
    df.loc[df['maxspeed'] < 20, 'maxspeed'] = 20
    if context != 'city':
        df['maxspeed'] = round(df['maxspeed'], -1)
    maxspeed_map = {20: 10, 30: 9, 40: 8, 50: 7, 60: 6, 70: 5, 80: 4, 90: 3, 100: 2, 110: 1}
    df['maxspeed'] = df['maxspeed'].map(maxspeed_map)

    # Lanes
    df.loc[df['lanes'] > 8, 'lanes'] = 8
    lanes_map = {1: 10, 2: 9, 3: 5, 4: 5, 5: 3, 6: 3, 7: 2, 8: 1}
    df['lanes'] = df['lanes'].map(lanes_map)

    # Oneway
    oneway_map = {0: 5, 1: 10, -1: 5}
    df['oneway'] = df['oneway'].map(oneway_map)

    # Width
    df.loc[df['width'] < 2, 'width'] = 1
    df.loc[df['width'] > 6, 'width'] = 6
    df['width'] = round(df['width'])
    width_map = {1: 1, 2: 2, 3: 5, 4: 7, 5: 9, 6: 10}
    df['width'] = df['width'].map(width_map)

    # Centrality normalization
    df['centrality'] = ((df['centrality'] - np.min(df['centrality'])) /
                        (np.max(df['centrality']) - np.min(df['centrality']))) * 10

    return df

def _apply_weights_and_index(df):
    """Apply weights and calculate bikeability index."""
    df['cycleway'] = df['cycleway'] * 0.208074534
    df['surface'] = df['surface'] * 0.108695652
    df['highway'] = df['highway'] * 0.167701863
    df['maxspeed'] = df['maxspeed'] * 0.189440994
    df['lanes'] = df['lanes'] * 0.108695652
    df['centrality'] = df['centrality'] * 0.071428571
    df['width'] = df['width'] * 0.086956522
    df['oneway'] = df['oneway'] * 0.059006211
    df['index'] = (np.nanmean(df[['cycleway', 'highway', 'surface', 'maxspeed',
                                  'lanes', 'width', 'oneway', 'centrality']], axis=1, dtype='float64')) * 80
    return df

def _make_grid(area, width=0.041667, height=0.041667):
    """Divide area into grid polygons."""
    xmin, ymin, xmax, ymax = area.total_bounds
    rows = int(np.ceil((ymax - ymin) / height))
    cols = int(np.ceil((xmax - xmin) / width))
    XleftOrigin = xmin
    XrightOrigin = xmin + width
    YtopOrigin = ymax
    YbottomOrigin = ymax - height
    polygons = []
    for i in range(cols):
        Ytop = YtopOrigin
        Ybottom = YbottomOrigin
        for j in range(rows):
            polygons.append(Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop),
                                     (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)]))
            Ytop -= height
            Ybottom -= height
        XleftOrigin += width
        XrightOrigin += width
    return polygons

def _filter_grid_within(area, polygons):
    """Keep only polygons that intersect or are within the area."""
    grid_list = []
    for poly in polygons:
        p = Point(poly.centroid.x, poly.centroid.y)
        geome = shape(poly)
        q = gpd.GeoDataFrame({'geometry': geome}, index=[0]).set_crs("EPSG:4326")
        if area.geometry.iloc[0].contains(poly):
            grid_list.append(q)
        elif area.geometry.iloc[0].intersects(poly):
            clip = gpd.clip(area, q)
            grid_list.append(clip)
    return grid_list

def _process_single_grid(grid, useful_tags_way):
    """Process a single grid polygon for bikeability scoring."""
    try:
        box_graph = _prepare_graph(None, useful_tags_way, 'bike', polygon=grid.geometry.iloc[0])
        _add_centrality(box_graph)
        edges = _extract_edges(box_graph)
    except Exception:
        return None, None
    cols = ['highway', 'cycleway', 'surface', 'maxspeed', 'length', 'lanes', 'oneway',
            'width', 'centrality', 'geometry']
    try:
        df = edges.loc[:, cols]
    except Exception:
        return None, None
    df['maxspeed'] = pd.to_numeric(df['maxspeed'], errors='coerce', downcast='integer')
    df['lanes'] = pd.to_numeric(df['lanes'], errors='coerce', downcast='integer')
    df['width'] = pd.to_numeric(df['width'], errors='coerce', downcast='unsigned')
    df['highway'] = df['highway'].astype(str)
    df['surface'] = df['surface'].astype(str)
    df['oneway'] = df['oneway'].astype(int)
    df['cycleway'] = df['cycleway'].astype(str)
    df = _clean_and_map_columns(df, context='grid')
    d_frame = df.copy(deep=True)
    d_frame = _apply_weights_and_index(d_frame)
    d_frame['grid_index'] = np.average(d_frame['index'], weights=d_frame['length'])
    return d_frame, df

def bikeability(place, scale='city', data=False):
    '''Calculate bikeability for a given place.

    Parameters
    ----------
    place : str
        Place of interest, e.g. "Freiburg, Germany"
    scale : str
        "grid" or "city" (default "city")
    data : bool
        If True, returns dataframe and result dictionary

    Returns
    -------
    dict or (pd.DataFrame, dict)
        Bikeability scores and statistics
    '''
    if scale != 'grid':
        # CITY SCALE APPROACH
        useful_tags_way = ['bridge', 'length', 'oneway', 'lanes', 'ref', 'name',
                           'highway', 'maxspeed', 'service', 'access', 'area', 'cycleway',
                           'landuse', 'width', 'est_width', 'junction', 'surface']
        graph = _prepare_graph(place, useful_tags_way, 'all')
        _add_centrality(graph)

        try:
            edges = _extract_edges(graph)
        except Exception as e:
            print(f'{e} at {place}')
            return None if not data else (None, None)

        cols = ['highway', 'cycleway', 'surface', 'maxspeed', 'length', 'lanes', 'oneway',
                'width', 'centrality', 'geometry']
        try:
            df = edges.loc[:, cols]
        except KeyError as e:
            print(e)
            return None if not data else (None, None)

        df['maxspeed'] = pd.to_numeric(df['maxspeed'], errors='coerce', downcast='integer')
        df['lanes'] = pd.to_numeric(df['lanes'], errors='coerce', downcast='integer')
        df['width'] = pd.to_numeric(df['width'], errors='coerce', downcast='unsigned')
        df['highway'] = df['highway'].astype(str)
        df['surface'] = df['surface'].astype(str)
        df['oneway'] = df['oneway'].astype(int)
        df['cycleway'] = df['cycleway'].astype(str)

        df = _clean_and_map_columns(df, context='city')
        d_frame = df.copy(deep=True)
        d_frame = _apply_weights_and_index(d_frame)

        mean_index = np.average(d_frame['index'], weights=d_frame['length'])
        max_index = d_frame['index'].max()
        min_index = d_frame['index'].min()
        std_index = d_frame['index'].std()
        result = {'place': place, 'average_index': mean_index, 'max_index': max_index,
                  'min_index': min_index, 'std_index': std_index}

    else:
        # GRID SCALE APPROACH
        area = ox.geocode_to_gdf(place)
        polygons = _make_grid(area)
        grid_list = _filter_grid_within(area, polygons)

        dflist = []
        exception_grids = []
        dfs = []
        useful_tags_way = ['bridge', 'length', 'oneway', 'lanes', 'ref',
                           'name', 'highway', 'maxspeed', 'surface', 'area',
                           'landuse', 'width', 'est_width', 'junction', 'cycleway']

        for i in tqdm(range(len(grid_list))):
            d_frame, df = _process_single_grid(grid_list[i], useful_tags_way)
            if d_frame is None:
                exception_grids.append(i + 1)
                continue
            dflist.append(d_frame)
            dfs.append(df)

        if len(dflist) == 0:
            result = {'place': place, 'average_index': None, 'max_index': None,
                      'min_index': None, 'std_index': None, 'grids': len(grid_list),
                      'nsegments': 0, 'unused_grids': len(exception_grids)}
            d_frame = None
        else:
            df_indexes = pd.concat(dflist)
            result = {'place': place,
                      'average_index': np.average(df_indexes['index'], weights=df_indexes['length']),
                      'max_index': df_indexes['index'].max(),
                      'min_index': df_indexes['index'].min(),
                      'std_index': df_indexes['index'].std(),
                      'grids': len(grid_list),
                      'nsegments': len(df_indexes),
                      'unused_grids': len(exception_grids)}
            d_frame = df_indexes

    return result if not data else (result, d_frame)