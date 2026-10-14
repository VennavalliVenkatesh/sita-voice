from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import logging
import os

app = FastAPI(title="SITA IndicXlit Transliteration Service")

# Allow CORS for client applications (Android app, local development, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.error")

# Global XlitEngine engines cache per language
engines = {}

class TranslitRequest(BaseModel):
    text: str
    language: str

@app.on_event("startup")
def load_model():
    # Lazy loading is used per language on demand
    logger.info("SITA IndicXlit Service starting up...")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "indicxlit-transliteration",
        "version": "1ec67a1-v2",
        "loaded_languages": list(engines.keys())
    }

@app.post("/transliterate")
def transliterate(request: TranslitRequest):
    text = request.text.strip()
    lang = request.language.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty or whitespace only.")
        
    valid_langs = {"hi", "te", "kn", "or"}
    if lang not in valid_langs:
        raise HTTPException(status_code=400, detail=f"Language code '{lang}' is not supported. Supported languages: {sorted(list(valid_langs))}")
        
    if lang not in engines:
        try:
            from ai4bharat.transliteration import XlitEngine
            logger.info(f"Initializing XlitEngine for '{lang}'...")
            # Initialize with beam_width=4 and rescore=True matching production configuration
            engines[lang] = XlitEngine(lang, beam_width=4, rescore=True)
            logger.info(f"XlitEngine for '{lang}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load XlitEngine for '{lang}': {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"XlitEngine failed to load: {str(e)}")
            
    engine = engines[lang]
        
    start_time = time.time()
    try:
        result = engine.translit_sentence(text)
        
        if isinstance(result, list) or isinstance(result, tuple):
            out_text = result[0]
        else:
            out_text = str(result)
            
    except Exception as e:
        logger.error(f"Transliteration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error during transliteration processing.")
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    logger.info(f"Processed transliteration request for language '{lang}' in {latency_ms}ms")
    
    return {
        "text": out_text,
        "language": lang,
        "latency_ms": latency_ms
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8100))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
