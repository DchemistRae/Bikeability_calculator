
def calc_bike_index(d_frame):

    '''Function accepts a dataframe input, calculates bikeability index
    and reurns a tuple with dataframe result at index 0 and average
    value for the city at index 1'''
    d_frame['surface_type'] = d_frame['surface_type'] * 0.1383399
    d_frame['waytypes'] = d_frame['waytypes'] * 0.2648221
    d_frame['steepness'] = d_frame['steepness'] * 0.1264822
    #suitability
    d_frame['maxspeed'] = d_frame['maxspeed'] * 0.2411067
    d_frame['lanes'] = d_frame['lanes'] *0.1383399
    #oneway
    d_frame['directness'] = d_frame['directness'] * 0.0909091

    #suitability and oneway were droped before calculating index
    d_frame.drop(['suitability','oneway'], axis=1, inplace=True)
    #sum of weighted variables from row index 3 >>>>always
    #check for correctness
    d_frame['summation'] = d_frame.iloc[:,3:].sum(axis=1)
    #Get a value between 0 and 100 for bikeability index (maximum weight is 60)
    d_frame['index'] = ((d_frame['summation'] * 100) /10)
    #Final average index of city
    mean_index = sum(d_frame['index'])/len(d_frame['index'])
    #list of weight
    weight_list = [0.2648221,0.2411067,0.1383399,0.1383399,0.1264822,0.0909091]

    return d_frame, mean_index
    

    ams = pd.read_csv('ams.csv')
    amsterdam_index = calc_bike_index(ams)
    amsterdam_index[0]
    amsterdam_index[1]

    bern_result = calc_bike_index(pd.read_csv('bern.csv'))
    bern_result[1]
    bern_result[0]

    test = calc_bike_index(pd.read_csv('test1.csv'))
    test[1]
    test[0]




