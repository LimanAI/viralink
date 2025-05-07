#!/usr/bin/env bash
set -euo pipefail

DIR="$(dirname "$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )")"

docker rm viralink-generate-openapi || true
docker run \
    --volume "${DIR}":/sdk \
    --name viralink-generate-openapi \
    openapitools/openapi-generator-cli:v7.13.0 \
    generate \
    -i /sdk/openapi.json \
    -g typescript-fetch \
    -o /sdk/src/client2
