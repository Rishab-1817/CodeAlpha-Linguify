import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from googletrans import Translator, LANGUAGES

app = FastAPI(
    title="Linguify API",
    description="Backend API for CodeAlpha-Linguify Language Translation Application",
    version="1.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Mount the static directory for CSS and JS assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Configure the templates directory for HTML files
templates = Jinja2Templates(directory="templates")

# Initialize the Googletrans Translator
translator = Translator()

# Pydantic models for request/response validation
class TranslationRequest(BaseModel):
    text: str
    src_lang: str = "auto"  # Default to auto-detect
    dest_lang: str

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    src_lang: str
    dest_lang: str

# --- FRONTEND ROUTES ---

# Serve index.html at the root URL
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# --- API ENDPOINTS ---

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok", 
        "message": "Language Translation API is running. Visit /docs for API docs."
    }

@app.get("/api/languages")
async def get_languages():
    """Returns a dictionary of all supported languages and their codes."""
    return {"supported_languages": LANGUAGES}

@app.post("/api/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translates text from source language to destination language."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text to translate cannot be empty.")
    
    # Validate destination language code
    if request.dest_lang not in LANGUAGES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid destination language code: '{request.dest_lang}'. Check /api/languages for valid codes."
        )
    
    # Validate source language code if it's not set to 'auto'
    if request.src_lang != "auto" and request.src_lang not in LANGUAGES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid source language code: '{request.src_lang}'. Use 'auto' or a valid code."
        )

    try:
        # Perform translation
        result = translator.translate(
            text=request.text, 
            src=request.src_lang, 
            dest=request.dest_lang
        )
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=result.text,
            src_lang=result.src,
            dest_lang=result.dest
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Read port from environment variable for hosting services like Railway
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
