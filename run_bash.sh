#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))

docker run --rm -it \
  -v $SCRIPT_PATH/data:/data \
  -v $SCRIPT_PATH/src:/app \
  -v /home/pi/ctreader-docker/data:/ctdata \
  -p 8050:8050 \
  dashmonitor /bin/bash

