#!/bin/bash

# Start react app from within mounted docker volume

cd tree-epi-front
echo "[i] Downloading yarn dep..."
yarn add env-cmd --ignore-engines  # needs to be run from inside correct folder
echo "[i] Staring tree epi front end..."
yarn start-docker-dev
