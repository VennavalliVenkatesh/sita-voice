#!/bin/bash
set -e

echo "=== Upgrading pip to 24.0 for stable legacy build support ==="
pip install "pip==24.0" setuptools wheel

echo "=== Pre-installing PyTorch CPU ==="
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo "=== Installing fairseq-fixed (pre-compiled modern wheel) ==="
pip install fairseq-fixed

echo "=== Installing remaining requirements ==="
pip install -r requirements.txt

echo "=== Build Complete ==="
