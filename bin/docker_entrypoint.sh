#!/bin/bash

echo "Rebuilding hnsw to ensure architecture compatibility"
pip install --force-reinstall --no-cache-dir mutant-hnswlib
export IS_PERSISTENT=1
uvicorn mutantdb.app:app --workers 1 --host 0.0.0.0 --port 8000 --proxy-headers --log-config log_config.yml