#!/bin/bash

# while getopts u:d:a:l:p: flag
# do
#     case "${flag}" in
#         u) uri_auth=${OPTARG};;
#         d) db_path=${OPTARG};;
#         a) admin_token=${OPTARG};;
#         l) address=${OPTARG};;
#         p) port=${OPTARG};;
#     esac
# done

# docker volume create dirdb


docker run --privileged -dti --name restfs -p $4:$4 -p $5:$5 -p $6:$6 --hostname restfs  josemimo2/restfs_full:latest $1 $2 $3 $4 $5 $6 $7 $8 $9

# ./run.sh -u https://auth.serv.com -d /db -a admin -l 0.0.0.0 -p 3002 