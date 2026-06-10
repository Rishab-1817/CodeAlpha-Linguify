from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from gtts import gTTS
import io
from fastapi.responses import StreamingResponse
import os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslateRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

# Language mapping
LANGUAGES = {
    'auto': 'Detect Language',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'tr': 'Turkish',
    'nl': 'Dutch',
    'pl': 'Polish',
    'vi': 'Vietnamese',
    'th': 'Thai'
}

@app.get("/")
async def root():
    # Serve the index.html file from static folder
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"status": "ok", "message": "Linguify API is running"}

@app.get("/api/languages")
async def get_languages():
    return LANGUAGES

@app.post("/api/translate")
async def translate(request: TranslateRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        source = request.source_lang if request.source_lang != 'auto' else 'auto'
        translator = GoogleTranslator(source=source, target=request.target_lang)
        translated = translator.translate(request.text)
        return {"translated_text": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts")
async def text_to_speech(text: str, lang: str):
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        tts_lang = lang if lang != 'auto' else 'en'
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return StreamingResponse(
            audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
