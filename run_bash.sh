#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))

docker run --rm -it \
  -v $SCRIPT_PATH/data:/data \
  -v $SCRIPT_PATH/src:/app \
  -v $SCRIPT_PATH/ipython:/root/.ipython \
  -v /home/pi/ctreader-docker/data:/ctdata \
  -v /home/pi/analyze/data:/analyze \
  allinone-py311 /bin/bash --rcfile /bashrc
  #-p 8050:8050 \

