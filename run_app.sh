#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))

docker run --rm \
  -v $SCRIPT_PATH/data:/data \
  -v $SCRIPT_PATH/src:/app \
  -v /home/pi/ctreader-docker/data:/ctdata \
  -p 8050:8050 \
  allinone-py311 python app.py

