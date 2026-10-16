library(objr)

args <- commandArgs(trailingOnly = TRUE)
uuid <- args[1]
folder <- args[2]
download_file(uuid, folder)
