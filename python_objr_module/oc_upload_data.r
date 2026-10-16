library(objr)

args <- commandArgs(trailingOnly = TRUE)
uuid <- args[1]
folder_uuid <- args[2]
filename <- args[3]
upload_file(filename, uuid, parent_uuid = folder_uuid)
