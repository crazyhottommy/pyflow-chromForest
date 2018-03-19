library(tidyverse)
library(purrr)
library(stringr)
options(scipen=500)

## important to write, R will change 400000 to 4e+05, this may cause troubles
# make it from a list to a vector
files<- unlist(snakemake@input)

file_list<- map(files, read_tsv, col_names =F)

seg_df<- purrr::reduce(file_list, left_join, by = c("X1", "X2", "X3"))

sample_names<- str_replace(basename(files),  "_recode_seg.bed", "")
colnames(seg_df)<- c("chr", "start", "end",  sample_names)
write.table(seg_df, snakemake@output[[1]], sep = "\t", col.names =T, row.names = F, quote =F)

epilogos_input<- seg_df %>% dplyr::mutate_at(4:ncol(.), funs(str_replace_all(., "E", "")))
write.table(epilogos_input, snakemake@output[[2]], sep = "\t", col.names =F, row.names = F, quote =F)
