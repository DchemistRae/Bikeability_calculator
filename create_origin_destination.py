  
import osmnx
import shapely
import random


def create_origin_destination_df(city_name, n_coords):
    boundary = osmnx.gdf_from_place(city_name)
    # if boundary is point not polygon try again with which_result = 2
    if not type(boundary.iloc[0].geometry) is shapely.geometry.polygon.Polygon:
        boundary = osmnx.gdf_from_place(city_name, which_result=2)

    print('Download Footrpint data for ' + city_name)
    buildings = osmnx.footprints.footprints_from_polygon(polygon=boundary.iloc[0].geometry, retain_invalid=False)  
    
    coords_list = []
    for i in range(n_coords):

        start_n = random.randint(1, len(buildings))
        start_x = buildings.iloc[start_n].geometry.centroid.x
        start_y = buildings.iloc[start_n].geometry.centroid.y

        end_n = random.randint(1, len(buildings))
        end_x = buildings.iloc[end_n].geometry.centroid.x
        end_y = buildings.iloc[end_n].geometry.centroid.y
        coords_list.append([[start_x, start_y], [end_x,end_y]])
    return coords_list

