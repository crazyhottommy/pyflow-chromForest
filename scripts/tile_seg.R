

library(GenomicRanges)
library(rtracklayer)
library(tidyverse)
options(scipen=500)

# it returns a list
seg<- snakemake@input[[1]]
bin_size<- snakemake@config[["bin_size"]]
bin_size<- as.numeric(bin_size)

chromHMM_seg<- import(seg, format = "BED")

tile_chromHMM<- function(chromHMM_seg, bin_size){
  chromHMM_seg_tile<- tile(chromHMM_seg, width = bin_size)
  names(chromHMM_seg_tile)<- chromHMM_seg$name
  stack(chromHMM_seg_tile, "state")
}


make_df<- function(gr){
  data.frame(chr = seqnames(gr), start = start(gr) - 1, end = end(gr), state = gr$state)
}

tile_seg<- tile_chromHMM(chromHMM_seg, bin_size)
tile_df<- make_df(tile_seg)

write.table(tile_df, snakemake@output[[1]], row.names =F, col.names =F, sep = "\t", quote =F)
