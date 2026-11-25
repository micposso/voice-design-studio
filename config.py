"""Environment configuration and shared workshop defaults."""
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

MODEL = "eleven_multilingual_v2"
MAX_CHARS = 1500
LANGUAGES = {"English": "en", "Spanish": "es", "French": "fr", "Italian": "it",
             "Portuguese": "pt", "German": "de", "Japanese": "ja", "Mandarin Chinese": "zh"}
TONES = ["Friendly", "Professional", "Calm", "Enthusiastic", "Reassuring", "Playful", "Neutral"]
DEFAULT_TEXT = "Hello! Welcome to our robotics laboratory. I am your robot assistant. I can help you explore our facilities, learn about robotics, and answer your questions. How can I help you today?"

@dataclass(frozen=True)
class Config:
    api_key: str = field(repr=False)
    voice_id: str
    ollama_model: str
    ollama_host: str

def load_config():
    load_dotenv(Path(__file__).with_name(".env"))
    return Config(os.getenv("ELEVENLABS_API_KEY", "").strip(),
                  os.getenv("ELEVENLABS_VOICE_ID", "").strip(),
                  os.getenv("OLLAMA_MODEL", "").strip(),
                  os.getenv("OLLAMA_HOST", "http://localhost:11434").strip() or "http://localhost:11434")
