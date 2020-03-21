import numpy as np
import pandas as pd

def weighted_avgfunc(var):
        var_wt =[]
        var_lst = []
        for x in range(len(var)):
            var_lst.append(var[x]['value'])
        for y in range(len(var)):
            var_amt = (var[y]['amount'])/100
            var_wt.append(var_amt)
        wt_var_avg =np.average(var_lst,weights=var_wt)
        return wt_var_avg
        
def weighted_mean(arr_lst,wt_lst):
    indices = ~np.isnan(arr_lst)
    avg_wt = np.average(arr_lst[indices],weights=wt_lst[indices])
    return avg_wt


