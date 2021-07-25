
 	Bikeability Tool
    A python function that calculate bikeability value for a given
    place of interest. 
    
  Parameters
    place(string): the place of interest e.g "Freiburg, Germany" datatype = string
    
    Scale(string): can be either "grid" or "city" default is "city" 
    
    data(boolean): if True output returns a dataframe along with the standard dictionary 
    output.
    
  Returns
    Results(dictionary): average_index for bikeability(number between 0 and 100) and some
    summary statistics of index. If dataframe arg = True, returns geodataframe.
    
    Usage example
    a = bikeability('Freiburg, Germany', scale ='grid', data = False) ... for grid scale approach
    a,b = bikeability('Freiburg, Germany', scale ='grid', data = True)
    a = bikeability('Freiburg, Germany', scale = 'city')... for city scale approach
    a,b = bikeability('Freiburg, Germany', scale = 'city', data = True)
    
    ******** Developed on python ver 3.6 **********
