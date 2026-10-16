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

echo "=== Pre-seeding IndicXlit model directories and manifests ==="
mkdir -p ai4bharat/transliteration/transformer/models/en2indic/v1.0
mkdir -p ai4bharat/transliteration/transformer/models/indic2en/v1.0
mkdir -p /opt/render/project/src/ai4bharat/transliteration/transformer/models/en2indic/v1.0 || true
mkdir -p /opt/render/project/src/ai4bharat/transliteration/transformer/models/indic2en/v1.0 || true
mkdir -p "$HOME/.AI4Bharat_Xlit_Models/en2indic/v1.0" || true
mkdir -p "$HOME/.AI4Bharat_Xlit_Models/indic2en/v1.0" || true

# Copy into models directory, v1.0 subfolder, and user cache
cp ai4bharat/transliteration/transformer/models/en2indic/lang_list.txt ai4bharat/transliteration/transformer/models/en2indic/v1.0/lang_list.txt || true
cp ai4bharat/transliteration/transformer/models/indic2en/lang_list.txt ai4bharat/transliteration/transformer/models/indic2en/v1.0/lang_list.txt || true
cp ai4bharat/transliteration/transformer/models/en2indic/lang_list.txt "$HOME/.AI4Bharat_Xlit_Models/en2indic/lang_list.txt" || true
cp ai4bharat/transliteration/transformer/models/en2indic/lang_list.txt "$HOME/.AI4Bharat_Xlit_Models/en2indic/v1.0/lang_list.txt" || true
cp ai4bharat/transliteration/transformer/models/indic2en/lang_list.txt "$HOME/.AI4Bharat_Xlit_Models/indic2en/lang_list.txt" || true
cp ai4bharat/transliteration/transformer/models/indic2en/lang_list.txt "$HOME/.AI4Bharat_Xlit_Models/indic2en/v1.0/lang_list.txt" || true

echo "=== Build Complete ==="
