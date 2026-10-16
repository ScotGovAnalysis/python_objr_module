library(objr)

args <- commandArgs(trailingOnly = TRUE)
filename <- args[1]
uuid <- args[2]
upload_file_version(filename, uuid)