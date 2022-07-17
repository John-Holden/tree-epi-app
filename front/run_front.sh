#!/bin/bash

# Start react app from within mounted docker volume
echo "[i] Staring tree epi front end..."
cd tree_epi_front && yarn start-docker-dev
