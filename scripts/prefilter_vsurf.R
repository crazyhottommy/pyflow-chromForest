
library(tidyverse)
library(readr)
options(scipen=500)

vsurf_bin_merged<- snakemake@input[[1]]

seg_df<- read.table(vsurf_bin_merged, header =T, stringsAsFactor = F)
seg_df_state<- dplyr::select(seg_df, -chr, -start, -end)

seg_df_state<- as.data.frame(seg_df_state)

## test if every column has the same string for every row
ind<- apply(seg_df_state, 1, function(x) length(unique(x)) == 1)

# keep only the rows that are not the same state across samples.
seg_df_sub<- seg_df[!ind, ]

# put the same index id for the same rows (same combination of states across samples)
seg_df_sub<- seg_df_sub %>% mutate(pattern = group_indices_(seg_df_sub, .dots = names(seg_df_sub)[-c(1:3)]))

vsurf_input<- seg_df_sub%>% distinct(pattern, .keep_all =T) %>% select(-pattern)

write.table(seg_df_sub, snakemake@output[[1]], sep = "\t", col.names =T, row.names = F, quote =F)
write.table(vsurf_input, snakemake@output[[2]], sep = "\t", col.names =T, row.names = F, quote =F)
