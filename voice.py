"""Reusable speech synthesis; no Streamlit dependency."""
from dataclasses import dataclass, asdict
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from config import MODEL, MAX_CHARS

class VoiceError(Exception):
    """Safe, student-facing synthesis error."""

@dataclass(frozen=True)
class Settings:
    speed: float = 1.0
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True

def generate_audio(text: str, api_key: str, voice_id: str, settings: Settings) -> bytes:
    if not api_key or not voice_id:
        raise VoiceError("Add your ElevenLabs API key and Voice ID to .env, then restart the app.")
    if not text.strip() or len(text) > MAX_CHARS:
        raise VoiceError("Enter between 1 and 1,500 characters.")
    try:
        client = ElevenLabs(api_key=api_key, timeout=60)
        chunks = client.text_to_speech.convert(
            voice_id=voice_id, text=text, model_id=MODEL,
            output_format="mp3_44100_128", voice_settings=VoiceSettings(**asdict(settings)),
            request_options={"max_retries": 0},
        )
        audio = chunks if isinstance(chunks, bytes) else b"".join(chunks)
        if not audio:
            raise VoiceError("ElevenLabs returned no audio. Try again when ready.")
        return audio
    except VoiceError:
        raise
    except Exception as exc:
        status = getattr(exc, "status_code", None)
        body = getattr(exc, "body", None)
        detail = body.get("detail", {}) if isinstance(body, dict) else {}
        code = detail.get("status", "") if isinstance(detail, dict) else ""
        if code in {"quota_exceeded", "insufficient_credits", "credit_limit_exceeded"} or status == 402:
            message = "Not enough ElevenLabs credits. Check your account balance."
        elif status == 401 or status == 403:
            message = "ElevenLabs authentication or permissions failed. Check your API key and voice access."
        elif status == 404 or code == "voice_not_found":
            message = "Voice ID not found. Check your custom voice in ElevenLabs."
        elif status == 429:
            message = "ElevenLabs rate limit reached. Wait before manually trying again."
        elif status in (400, 422):
            message = "ElevenLabs rejected the request. Check the voice, model and settings."
        else:
            message = "Speech generation failed. Check your internet connection and ElevenLabs status."
        raise VoiceError(message) from None
