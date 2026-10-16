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

# Pre-download the core 126MB transformer model during build time so runtime never times out
MODEL_ZIP_URL="https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/indicxlit-en-indic-v1.0.zip"
TARGET_MODEL_DIR="ai4bharat/transliteration/transformer/models/en2indic/v1.0"
if [ ! -f "$TARGET_MODEL_DIR/transformer/indicxlit.pt" ]; then
    echo "=== Pre-downloading IndicXlit core model during build ==="
    curl -L "$MODEL_ZIP_URL" -o /tmp/model.zip
    unzip -q /tmp/model.zip -d "$TARGET_MODEL_DIR"
    rm -f /tmp/model.zip
    echo "=== Model pre-downloaded and unpacked successfully ==="
fi

# Pre-download lightweight RNN models for instant startup
RNN_DIR="ai4bharat/transliteration/rnn/models/v0.5"
mkdir -p "$RNN_DIR"
for l in telugu hindi; do
    if [ ! -d "$RNN_DIR/$l" ]; then
        echo "=== Pre-downloading RNN model for $l ==="
        curl -L "https://github.com/AI4Bharat/IndianNLP-Transliteration/releases/download/xlit_v0.5.0/$l.zip" -o "/tmp/$l.zip"
        unzip -q "/tmp/$l.zip" -d "$RNN_DIR"
        rm -f "/tmp/$l.zip"
    fi
done

echo "=== Build Complete ==="
