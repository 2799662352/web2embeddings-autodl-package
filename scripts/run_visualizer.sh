#!/bin/bash
set -e

# Run the visualization script with default parameters
# Users can modify these parameters as needed
python src/visualizer.py \
    --db /root/autodl-tmp/artifacts/vector_stores/chroma_db \
    --collection "danbooru_training_data_jina-embeddings-v3" \
    --max-points 2000 \
    --seed 42 \
    --clusters 10 \
    --outlier-threshold 3.0 