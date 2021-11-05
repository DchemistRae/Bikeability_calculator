# Bikeability Calculator Tool


An automated bikeabililty assessment tool, a python package that outputs
bikeability index as values and map after evaluating all road segments in a given place.


## Description

Our tool is a functional
python script built on top the OSMnx package. This tool automates the entire process of
downloading OpenStreetMap data, cleaning and processing the data, it also assigns values and
weights to road segments, before finally evaluating bikeability and providing an output in form of
an integer value or geopandas dataframe that can be ploted for visualization.

This tool uses two approaches to calculate bikeability of the place of interest, approach given as a hyperparameter;
1. Calculation based on entire place of interest e.g all bikable road within the city
2. Calculation using a grid system over the place of interest, bikeability for each grid is calculated and averaged across the area.


## Getting Started

### Dependencies

* Python 3.6 or above
* OSMNx
* tqdm
* Networkx
* Shapely
* Geopandas & Pandas
* Numpy


### Installing

* Install the dependencies above and install from github
```
pip install -e git+https://github.com/DchemistRae/Bikeability_calculator#egg=bikeability
```


### Executing program

* Method 1 - This will return an index using approach 1 described above
```
fr_index = bikeability('Freiburg, Germany')
```
* Method 2 - This will return an index using approach 2 described above
```
fr_grided_index = bikeability('Freiburg, Germany', scale = grid)
```
* Method 3 - This will return a geopandas dataframe of along with index
```
fr_index, gpd_df = bikeability('Freiburg, Germany', data = True)
```


## Parameters

- `place`

    (str, list of str) place of interest e.g 'Freiburg, Germany'.

- `scale`

    (str {'city', 'grid'}) This will choose either approach 1 or 2.
    Default: `'city'`

- `data`

    (boolean) This will return a geopandas dataframe of along with index. the dataframe can be plotted for visualization.
    Default: `False`

-`Returns` <br />
    (Dictionary) Contains index value between 0 and 100 (100 is highest 0 is lowest) along some statistical information. <br />
    (Geodataframe) Contains road segments information within the place of interest along with index.


## Authors

Dchemist_Rae , [@Dchemist_Rae](https://twitter.com/dchemist_rae)

JesJehle

## Version History

* 0.0.1
    * Initial Release

## License

This project is licensed under the MIT Open-Source License - see the LICENSE.txt file for details

## References

* [Loidl & Zagel (2014)](https://www.researchgate.net/profile/Bernhard-Zagel/publication/269408093_Wie_sicher_ist_sicher-Innovatives_Kostenmodell_zur_Ermittlung_des_Gefahrdungspotenzials_auf_Radwegen/links/5572151408aeb6d8c0166ca0/Wie-sicher-ist-sicher-Innovatives-Kostenmodell-zur-Ermittlung-des-Gefaehrdungspotenzials-auf-Radwegen.pdf)
* [Winters et. al (2013)](https://journals.sagepub.com/doi/abs/10.1068/b38185)
