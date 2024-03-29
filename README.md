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
* tqdm
* Shapely
* Geopandas & Pandas
* Numpy
* OSMNx


### Installing

* Install the dependencies above and install this github repository using the snippet below
```
pip install -e git+https://github.com/DchemistRae/Bikeability_calculator#egg=bikeability
```


### Executing program

* Import the installed module
```
from bikeability.bikeability import bikeability
```
* Run the tool : Default usage
```
fr_index = bikeability('Freiburg, Germany')
```
* Run the tool : If geodataframe is required
```
fr_index, gpd_df = bikeability('Freiburg, Germany', scale = 'city', data = True)
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

* Asimhi R. (2020), Dynamic approach to evaluate Bikeability using Open-source data, MSc thesis, Albert Ludwig University, [Unpublished master's thesis].
* [Loidl & Zagel (2014)](https://www.researchgate.net/profile/Bernhard-Zagel/publication/269408093_Wie_sicher_ist_sicher-Innovatives_Kostenmodell_zur_Ermittlung_des_Gefahrdungspotenzials_auf_Radwegen/links/5572151408aeb6d8c0166ca0/Wie-sicher-ist-sicher-Innovatives-Kostenmodell-zur-Ermittlung-des-Gefaehrdungspotenzials-auf-Radwegen.pdf)
* [Winters et. al (2013)](https://journals.sagepub.com/doi/abs/10.1068/b38185)

## Results Screenshots
![Screenshot - 1](https://github.com/DchemistRae/Bikeability_calculator/blob/master/results/1-Some%20results%20from%20tool.png)
