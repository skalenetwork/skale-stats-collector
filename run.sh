#!/usr/bin/env bash

set -e

: "${ETH_ENDPOINT?Need to set ETH_ENDPOINT}"
: "${PROXY_DOMAIN?Need to set PROXY_DOMAIN}"

export FLASK_APP_HOST=0.0.0.0
export FLASK_APP_PORT=5000
export FLASK_HOST_PORT=${API_PORT:-3009}

docker-compose up -d --build