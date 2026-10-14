# SITA IndicXlit Transliteration Service

Standalone FastAPI backend microservice for offline-capable, neural Indic transliteration powered by AI4Bharat's `IndicXlit`.

---

## 1. Purpose of the Service
This service converts phonetic Roman/English characters into native Indic scripts (e.g., typing `"namaste"` yields `"नमस्ते"` or `"kiran"` yields `"కిరణ్"`).

> **CRITICAL DISTINCTION — TRANSLITERATION vs TRANSLATION:**
> - **Transliteration (THIS SERVICE):** Converts script / spelling while preserving phonetics and pronunciation across alphabets (e.g., Roman `"namaste"` $\to$ Devanagari `"नमस्ते"`). It **does not** translate meaning into English.
> - **Translation (NOT THIS SERVICE):** Converts words between different languages based on semantic meaning (e.g., `"नमस्ते"` $\to$ `"Hello"`). Translation in SITA is handled separately on-device by Google ML Kit.

**Remote Call Architecture:**
The SITA Android/Expo mobile application will call this service remotely over HTTP once deployed to Render (or when hosted locally during development).

---

## 2. Architecture & Components
```
                    +-----------------------------+
                    |  SITA Mobile / Voice Client |
                    |      (React Native / Expo)  |
                    +--------------+--------------+
                                   |
                         HTTP POST /transliterate
                         (JSON: text, language)
                                   v
                    +-----------------------------+
                    |       FastAPI Backend       |
                    |     (main.py on Render)     |
                    +--------------+--------------+
                                   |
                       XlitEngine (AI4Bharat)
                       - IndicXlit Transformer
                       - Beam search (width=4)
                       - Word prob rescoring (alpha=0.9)
                                   v
                    +-----------------------------+
                    |       Transliterated        |
                    |        Indic Script         |
                    +-----------------------------+
```

### Supported Languages:
- `hi` — Hindi (हिन्दी)
- `te` — Telugu (తెలుగు)
- `kn` — Kannada (ಕನ್ನಡ)
- `or` — Odia (ଓଡ଼ିଆ)

---

## 3. Runtime & Prerequisites
- **Python Version:** `3.10.x` (Python 3.10.12 recommended; compatibility verified with Python 3.10).
- **RAM / Memory Requirement:** Minimum **1 GB - 2 GB RAM** on the host instance (AI models and rescoring dictionaries require ~500 MB - 1 GB in memory per active language engine).

---

## 4. Installation & Local Setup

### Step 1: Create a Python Virtual Environment
```bash
python3.10 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# OR on Windows:
# .venv\Scripts\activate
```

### Step 2: Install Required Packages
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## 5. Running the Service Locally

Startup command using the actual entry point:
```bash
uvicorn main:app --host 0.0.0.0 --port 8100 --reload
```
Or run directly via Python:
```bash
python main.py
```

The service will be accessible at:
- **Health Check:** `http://localhost:8100/health`
- **Interactive OpenAPI Docs (Swagger UI):** `http://localhost:8100/docs`
- **Transliteration Endpoint:** `http://localhost:8100/transliterate`

---

## 6. Model Loading & Assets
The underlying `ai4bharat` engine uses lazy-loading on first invocation for each language:
- When a language engine is first queried (e.g., `te`), `XlitEngine` checks for local model weights.
- If not pre-cached, it automatically fetches the official AI4Bharat release assets:
  - **Weights ZIP:** `https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/indicxlit-en-indic-v1.0.zip`
  - **Dictionary ZIP:** `https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/word_prob_dicts.zip`
- Assets are cached in `~/.AI4Bharat_Xlit_Models/en2indic/v1.0/` or local `ai4bharat/transliteration/transformer/models/`.

---

## 7. API Reference

### 7.1 Health Check
- **Method:** `GET`
- **Path:** `/health`
- **Description:** Verifies service availability and lists currently initialized language engines.

**Response:**
```json
{
  "status": "healthy",
  "service": "indicxlit-transliteration",
  "loaded_languages": ["te", "hi"]
}
```

---

### 7.2 Transliterate Text
- **Method:** `POST`
- **Path:** `/transliterate`
- **Headers:** `Content-Type: application/json`

#### Request JSON Schema:
```json
{
  "text": "string (Required: Romanized Indic text)",
  "language": "string (Required: 'hi' | 'te' | 'kn' | 'or')"
}
```

#### Response JSON Schema:
```json
{
  "text": "string (Transliterated script in target language)",
  "language": "string (Target language code)",
  "latency_ms": "integer (Execution duration in milliseconds)"
}
```

#### Example 1: Hindi
**Request:**
```bash
curl -X POST "http://localhost:8100/transliterate" \
     -H "Content-Type: application/json" \
     -d '{"text": "mujhe bukhar hai", "language": "hi"}'
```
**Response:**
```json
{
  "text": "मुझे बुखार है",
  "language": "hi",
  "latency_ms": 115
}
```

#### Example 2: Telugu
**Request:**
```bash
curl -X POST "http://localhost:8100/transliterate" \
     -H "Content-Type: application/json" \
     -d '{"text": "naku jvaram vachindi", "language": "te"}'
```
**Response:**
```json
{
  "text": "నాకు జ్వరం వచ్చింది",
  "language": "te",
  "latency_ms": 128
}
```

---

## 8. Deployment on Render

### Step-by-Step Instructions:
1. **Push to Git Repository:**
   Push this standalone directory (`sita-indicxlit-service-share`) to a private GitHub/GitLab repository.
2. **Create New Web Service on Render:**
   - Go to [dashboard.render.com](https://dashboard.render.com).
   - Click **New +** $\to$ **Web Service**.
   - Connect your repository.
3. **Configure Settings:**
   - **Name:** `sita-indicxlit-service`
   - **Environment:** `Python`
   - **Region:** Choose closest to your target users (e.g., `Singapore` or `Frankfurt`/`Oregon`).
   - **Branch:** `main`
   - **Build Command:**
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type / Plan:**
     - Select **Starter** (512MB - 2GB RAM) or higher.
     - *Note:* Render Free tier (512 MB) may experience OOM (Out Of Memory) or cold starts if multiple Indic language models are loaded concurrently.
4. **Environment Variables:**
   - `PYTHON_VERSION`: `3.10.12`
   - (No API keys or secrets are required; the service runs entirely open-source offline models).

---

## 9. Important Notes for the AI / Backend Team
1. **Cold Start & Model Download:**
   The first transliteration request after deployment triggers the one-time download and caching of the IndicXlit checkpoint (~700MB) from GitHub releases. Initial response latency will be higher (~20-40 seconds); subsequent calls take ~30-150ms.
2. **Port Handling:**
   Render automatically assigns an ephemeral port via the `$PORT` environment variable. `main.py` is configured with `os.environ.get("PORT", 8100)` and `uvicorn main:app --host 0.0.0.0 --port $PORT` respects this natively.
3. **CORS:**
   FastAPI CORS middleware is enabled (`allow_origins=["*"]`) so your React Native / Expo mobile app or web dashboards can invoke the service directly.
