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
*  -b: buckets for different energy flow potential scores (how close do scores have to be in order to be treated as similar?): [upper boundary for closest score (exclusive), upper boundary for medium score (exclusive)]

Examples and standard values:
```
-s "[1.0, 0.5, 0.3]"  
-t "[1.0, 0.3, 0.5, 0.1]"
-f "sum"
-b "[2, 5]"
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

#### Complementarity of flow volumes
*  HS-[In|Out]-Low vs. HS-[In|Out]-High: assign a constant variable specifying the order of magnitude of "high" being greater than "low" similar to low, medium and high inputs and outputs being represented by values of 1, 2 and 3, respectively

### Scoring
*  define thresholds and scores for bins, e.g. if the difference between energy input and output of a certain type is in a pre-defined range, assign a pre-defined score
    *  define relative scores, e.g. factory 1 outputs 30-50% of the energy needed by factory 2: assign score X
*  use relative scores directly as discounting factors

#### Similarity of materials
*  require material codes to be equal
*  use graph-based similarity measure 

#### Scoring
*  define thresholds and scores for bins, e.g. two parent nodes equal: score 1. One parent node equal: score 2. 
*  continuous values: use output of similarity measure directly to normalize score (can be different from 1 when e.g. number of siblings is factored in by the measure)
*  combination of material similarity and volumes: how to weight small flow potential of very similar products vs. greater flow potential of less similar products?

## Troubleshooting
*  import error:  
   may be caused by Excel not adhering to file format standards. Try saving the xlsx file using libreoffice or remove colour highlights
