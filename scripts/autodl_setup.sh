#!/bin/bash
set -e

# Update pip
python -m pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt

echo "Setup complete. Environment is ready." 