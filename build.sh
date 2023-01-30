#!/usr/bin/bash

docker build --platform linux/amd64 -f docker/Dockerfile --tag josemimo2/restfs_full:latest docker/

#docker save josemimo2/debian-dirapi:latest | gzip > debian-dirapi_latest.tar.gz
# ./build.sh