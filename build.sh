#!/bin/bash
set -e

echo "=== Upgrading pip to <24.1 for Fairseq compatibility ==="
pip install "pip<24.1" setuptools wheel

echo "=== Pre-installing PyTorch CPU ==="
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo "=== Installing patched Fairseq without hydra conflict ==="
if [ ! -d "fairseq" ]; then
    git clone https://github.com/pytorch/fairseq.git
fi
cd fairseq
sed -i 's/"hydra-core>=1.0.7,<1.1"/"hydra-core>=1.0.7"/g' setup.py
sed -i 's/"omegaconf<2.1"/"omegaconf>=2.0.5"/g' setup.py
pip install --no-build-isolation -e .
cd ..

echo "=== Installing remaining requirements ==="
pip install -r requirements.txt

echo "=== Build Complete ==="
