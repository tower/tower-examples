#!/bin/bash
set -ex

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

docker build -t iceberg-loader .

docker run -d \
  --name iceberg-loader \
  --log-driver=awslogs \
  --log-opt awslogs-region=eu-central-1 \
  --log-opt awslogs-group=/ec2/iceberg-loader \
  -e PYICEBERG_CATALOG__DEFAULT__CREDENTIAL \
  -e PYICEBERG_CATALOG__DEFAULT__URI \
  -e PYICEBERG_CATALOG__DEFAULT__WAREHOUSE \
  -e PYICEBERG_CATALOG__DEFAULT__SCOPE \
  -e TABLE_NAME=CATALOG_RETURNS \
  -e BUCKET_NAME=snowflake-iceberg-stage \
  iceberg-loader
