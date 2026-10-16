library(objr)
library(jsonlite)

args <- commandArgs(trailingOnly = TRUE)
uuid <- args[1]
df <- versions(uuid)

cat(toJSON(df, dataframe = "rows", auto_unbox = TRUE))