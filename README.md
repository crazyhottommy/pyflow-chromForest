# pyflow_epilogos
snakemake workflow for epilogos on chromHMM data


```bash
ssh railab
screen
source activate py351
# some R packages only for this R version
module load R/3.4.1-shlib

# dry run
snakemake -np

# submit to cluster 
./pyflow-epilogos
```
