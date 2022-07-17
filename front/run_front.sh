#!/bin/bash

# Start react app from within mounted docker volume
echo "[i] Staring tree epi front end..."
cd tree-epi-front && yarn start-docker-dev
