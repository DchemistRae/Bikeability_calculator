
 	Bikeability Tool
    A python function that calculate bikeability value for a given
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
    a = bikeability('Freiburg, Germany', scale = 'city')... for city scale approach
    a,b = bikeability('Freiburg, Germany', scale = 'city', data = True)
