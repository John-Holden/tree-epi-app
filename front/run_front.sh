#!/bin/bash

# Start react app from within mounted docker volume
echo "[i] Staring tree epi front end..."
y2racc2.7
cd tree-epi-front && yarn start-docker-dev
