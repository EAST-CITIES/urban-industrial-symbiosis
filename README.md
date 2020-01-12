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

## Troubleshooting
*  import error:  
   may be caused by Excel not adhering to file format standards. Try saving the xlsx file using libreoffice or remove colour highlights
