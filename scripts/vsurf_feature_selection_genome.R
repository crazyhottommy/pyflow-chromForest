library(VSURF)
library(purrr)

rdas<- snakemake@input[["rdas"]]

get_thres_featurs<- function(rda){
  load(rda)
  rf_mat<- x_data[,vsurf$varselect.thres]
}

new_data<- map(rdas, get_thres_featurs)
x_data<- purrr::reduce(new_data, cbind)

meta_data<- read.table(snakemake@input[["meta_data"]],stringsAsFactors = F, sep = "\t", header = T)

resp_data<- merge(x = data.frame(sample = rownames(x_data)), y = meta_data, by.x = "sample", by.y = "sample", all.x = T, all.y = F)
resp_data[,2]<- as.factor(resp_data[,2])

# it is critical to turn the response to factor to let VSURF know you are doing classification rather than regression.
vsurf = VSURF(x = x_data, y = resp_data[,2], ntree = 500, parallel =T, ncore = 12)
save(x_data, resp_data, vsurf, file = snakemake@output[[1]])
