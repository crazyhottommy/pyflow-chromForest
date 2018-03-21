library(VSURF)

chr<- snakemake@params[["jobname"]]
new_data<- read.table(snakemake@input[["vsurf_input"]], stringsAsFactors = F, sep = "\t", header = T)
meta_data<- read.table(snakemake@input[["meta_data"]],stringsAsFactors = F, sep = "\t", header = T)
x_data<- as.matrix(new_data[, -c(1:3)])

rownames(x_data)<- paste(new_data$chr, new_data$start, new_data$end, sep = ":")

## transpose the matrix.
x_data<- t(x_data)

## random forest does not like matrix if it is not numeric. turn back to a dataframe
x_data<- data.frame(x_data)

resp_data<- merge(x = data.frame(sample = rownames(x_data)), y = meta_data, by.x = "sample", by.y = "sample", all.x = T, all.y = F)
resp_data[,2]<- as.factor(resp_data[,2])

# it is critical to turn the response to factor to let VSURF know you are doing classification rather than regression.
vsurf = VSURF(x = x_data, y = resp_data[,2], ntree = 500, parallel =T, ncore = 24))
save(x_data, vsurf, file = snakemake@output[[1]])
