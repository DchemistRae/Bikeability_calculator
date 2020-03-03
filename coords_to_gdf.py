from shapely.geometry import Point
import pandas as pd
from geopandas import GeoDataFrame

df = pd.DataFrame.from_dict(df_dic)
# 1. get df with xy as columns (as strings)
geometry = [Point(xy) for xy in zip(df.x, df.y)]
# 2. create list of Points 
df['geometry'] = geometry
# 3. Replaces/create geometry in df
df_gdf = GeoDataFrame(df, geometry='geometry')
# set geometry column as geometry to create gdf
df_gdf.crs = {'init': 'epsg:4326'}
# set crs