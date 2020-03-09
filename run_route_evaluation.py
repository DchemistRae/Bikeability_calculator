from create_origin_destination import create_origin_destination_df
from evaluate_route import route_df

coords_l = create_origin_destination_df('Emmendingen, Germany', 20)


# stuttgart_airport =[[9.19515,48.690494],[7.850182, 47.99501]]
# points = [[7.854559, 48.003247],[7.850182, 47.99501]]
# 
ors_key = '5b3ce3597851110001cf6248480fc21010a54f35ad5e49b6d97490fb'
test = route_df(coords_l[0],ors_key)

