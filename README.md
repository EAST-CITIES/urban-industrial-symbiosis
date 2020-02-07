# urban-industrial-symbiosis

## About
(...)

## Usage
To output pairwise symbiosis potential scores:
```
python symbiosis/cluster.py -a <path to xlsx file containing the association tables> -c <path to xlsx file containing company data> 
```

Optional parameters:
*  -s: scores for energy input and output overlaps: [exact match input and output, divergence of 1, divergence of 2]
*  -t: scores for material input and output overlaps: [perfect_match(product and volume), partial_match (similar product, same volume), product_match (different volume), minimal_match (similar product, different volume)]
*  -f: function to accumulate symbiosis potential scores into final score

Examples and standard values:
```
-s "[1.0, 0.5, 0.3]"  
-t "[1.0, 0.3, 0.5, 0.1]"
-f "sum"
```

## Scoring

### Factors influencing the flow potentials

#### Size
The bigger a factory, the more energy and material is needed and the more products and waste are produced.
* use proportional factor: a factory twice as big as another one will have twice as large values. 

#### Year of establishment at site
The newer a factory, the lesser the energy consumption and waste output. 
*  use current year as pivot point, add penalties to energy consumption and waste output values for older years (e.g. +0.2% per year of age)
*  create bins: add penalty for certain groups, e.g. for all factories built before the year 2000, another penalty for all factories built before 1990 etc.

#### (Location)
(not factored in yet)
Close and well connected factories should be preferred.
*  Proximity: air-line distance
*  Transport connections: route networks including railways connecting the factories

### Flow comparisons and thresholds

#### Similarity of materials
*  require material codes to be equal
*  use graph-based similarity measure 

#### Scoring
*  define thresholds and scores for bins e.g. two parent nodes equal: score 1. One parent node equal: score 2. 
*  continuous values: use output of similarity measure directly to normalize score (can be different from 1 when e.g. number of siblings is factored in by the measure)

#### Complementarity of flow volumes
*  

## Troubleshooting
*  import error:  
   may be caused by Excel not adhering to file format standards. Try saving the xlsx file using libreoffice or remove colour highlights
