# urban-industrial-symbiosis

## About
Rapid analysis of potential symbiotic exchange flows based on a simplified parameter set combined with a typology/classification database


## Usage
To output pairwise symbiosis potential scores:
```
python symbiosis/cluster.py -a <path to xlsx file containing the association tables> -c <path to xlsx file containing company data> 
```

Optional parameters:
*  -e: energy flow scaling function; determines the impact of the company size on energy flow values
*  -m: material flow scaling function; determines the impact of the company size on material flow values
*  -y: energy flow scaling function; determines the impact of the factory's year of establishment on energy flow values
*  -z: material flow scaling function; determines the impact of the factory's year of establishment on material flow values
*  -f: function to accumulate symbiosis potential scores into final score
*  -s: scoring scheme materials; scores for input and output overlaps depending on whether materials are equal or similar

Examples and standard values:
```
-e "lambda x:float(x) / 100"
-m "lambda x:float(x) / 100"
-f "sum"
-s "[1.0, 0.3]"  
```

## Scoring

### Factors influencing the flow potentials

#### Size
The bigger a factory, the more energy and material is needed and the more products and waste are produced.
* use proportional factor: a factory twice as big as another one will have twice as large values. 
* choose one standard size; normalize all scores w.r.t their proportional relation to the standard

#### Year of establishment at site
The newer a factory, the lesser the energy consumption and waste output. 
*  use current year as pivot point, add penalties to energy consumption and waste output values for older years (e.g. +0.2% per year of age)
*  choose older year as pivot point, reduce energy consumption and waste output values for newer years (e.g. -0.2% per year)
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
