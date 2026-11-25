"""Reachy Voice Lab: explicit generation actions, persistent session recordings."""
import json
from dataclasses import asdict
from datetime import datetime
import streamlit as st
from config import load_config, DEFAULT_TEXT, LANGUAGES, TONES, MODEL, MAX_CHARS
from voice import Settings, VoiceError, generate_audio
from conversation import Personality, ConversationError, check_server, generate_response, add_message

st.set_page_config(page_title="Reachy Voice Lab", layout="wide")
config = load_config()
s = st.session_state
defaults = {"tone": "Friendly", "language": "English", **asdict(Settings())}
for key, value in {**defaults, "samples": [], "history": [], "latest": None, "final": None}.items():
    if key not in s:
        s[key] = value

def reset_settings():
    s.update(defaults)

def settings():
    return Settings(**{key: s[key] for key in asdict(Settings())})

def snapshot(personality):
    return {"voice_id": config.voice_id, "model": MODEL, "voice_settings": asdict(settings()),
            "tone": s.tone, "voice_language": s.language, "language_code": LANGUAGES[s.language],
            "robot_personality": asdict(personality)}

def record(text, metadata):
    audio = generate_audio(text, config.api_key, metadata["voice_id"], Settings(**metadata["voice_settings"]))
    return {"text": text, "audio": audio, "configuration": metadata,
            "created": datetime.now().astimezone().isoformat(timespec="seconds")}

def show_record(item):
    st.audio(item["audio"], format="audio/mp3")
    st.caption(item["created"])
    st.text(item["text"])
    with st.expander("Voice settings used"):
        st.json(item["configuration"])

def synthesize(text, metadata):
    try:
        with st.spinner("Generating speech..."):
            return record(text, metadata)
    except VoiceError as exc:
        st.error(str(exc))
        return None

st.title("Reachy Voice Lab")
st.caption("ARTI 609 — Designing Voice Experiences for Social Robots")
with st.sidebar:
    st.header("Configuration")
    st.write("ElevenLabs API key: " + ("Configured (not verified)" if config.api_key else "Missing"))
    st.write("Custom Voice ID: " + ("Configured (not verified)" if config.voice_id else "Missing"))
    if not config.api_key or not config.voice_id:
        st.info("Complete .env and restart the app to enable speech.")
    if st.button("Refresh connections") or "connection" not in s:
        s.connection = check_server(config.ollama_host)
    online, models = s.connection
    st.write("Ollama server: " + ("Available" if online else "Unavailable"))
    if models:
        if s.get("selected_model") not in models:
            s.selected_model = config.ollama_model if config.ollama_model in models else models[0]
        selected = st.selectbox("Selected Ollama model", models, key="selected_model")
    else:
        selected = None
        st.caption("Selected Ollama model: none")
        st.info("Start Ollama, install a model if needed, and refresh. Voice Studio still works.")
    st.caption("Speech model: " + MODEL)
    st.caption("Speech requests use ElevenLabs credits. Conversation text is generated locally.")

studio, chat, export = st.tabs(["Voice Studio", "AI Conversation", "Export MP3"])
# Render design controls first so the current settings are available to every tab.
with studio:
    st.header("Calibrate your robot voice")
    with st.expander("Six voice design principles", expanded=True):
        for title, description in [
            ("Tone", "Emotional attitude and delivery."),
            ("Pitch", "Perceived highness or lowness of the voice."),
            ("Timbre", "Texture and distinctive quality of the voice."),
            ("Accent", "Regional and cultural pronunciation characteristics."),
            ("Language", "Linguistic characteristics and pronunciation."),
            ("Rhythm and pacing", "Speech speed, pauses and timing."),
        ]:
            st.markdown(f"**{title}** — {description}")
    st.subheader("Design choices")
    left, right = st.columns(2)
    left.selectbox("Tone", TONES, key="tone")
    right.selectbox("Language", list(LANGUAGES), key="language")
    st.caption("Tone guides dialogue wording, not an API emotion setting. Language is detected from the written text by Multilingual v2; selecting a language does not translate it.")
    suggestions = {"Friendly": "Welcome! How can I help you today?", "Professional": "Welcome to the laboratory. How may I assist you?",
                   "Calm": "Take your time. I'm here to help.", "Enthusiastic": "Welcome! Let's explore robotics together!",
                   "Reassuring": "It's okay to have questions. We can work through them together.",
                   "Playful": "Ready to explore? Let's discover something new!", "Neutral": "Hello. What would you like to know?"}
    st.caption("Suggested dialogue (English example): " + suggestions[s.tone])
    st.subheader("ElevenLabs voice settings")
    st.caption("Pitch, timbre and accent primarily come from your custom voice and cannot be independently adjusted here.")
    left, right = st.columns(2)
    left.slider("Speed", 0.7, 1.2, step=0.05, key="speed")
    left.slider("Stability", 0.0, 1.0, step=0.05, key="stability")
    right.slider("Similarity boost", 0.0, 1.0, step=0.05, key="similarity_boost")
    right.slider("Style exaggeration", 0.0, 1.0, step=0.05, key="style")
    st.toggle("Speaker boost", key="use_speaker_boost")
    st.button("Reset Settings", on_click=reset_settings)
    text = st.text_area("Test script", DEFAULT_TEXT, max_chars=MAX_CHARS, height=130)
    st.caption(f"{len(text):,} / {MAX_CHARS:,} characters")
    generate = st.button("Generate Voice", type="primary", disabled=not text.strip())
    preview = st.container()
    comparison = st.container()

with chat:
    st.header("Design your robot personality")
    with st.expander("Robot personality configuration", expanded=True):
        name = st.text_input("Robot name", "Reachy")
        role = st.text_input("Robot role", "University robotics laboratory assistant.")
        traits = st.text_input("Personality", "Friendly, curious and helpful")
        style = st.text_input("Communication style", "Clear and conversational")
        response_language = st.selectbox("Response language", ["Use Voice Studio language", *LANGUAGES])
        instructions = st.text_area("Additional behavioral instructions")
    personality = Personality(name, role, traits, style,
                              s.language if response_language == "Use Voice Studio language" else response_language,
                              instructions)

metadata = snapshot(personality)
with preview:
    if generate:
        result = synthesize(text, metadata)
        if result:
            s.latest = result
    if s.latest:
        st.subheader("Latest recording")
        show_record(s.latest)
        sample_name = st.text_input("Sample name", placeholder=f"Sample {len(s.samples)+1}")
        if st.button("Save Sample"):
            s.samples.append({**s.latest, "name": sample_name.strip() or f"Sample {len(s.samples)+1}"})
            st.success("Sample saved.")
with comparison:
    st.subheader(f"Compare samples ({len(s.samples)} saved)")
    st.caption("Save at least three recordings. Replaying them does not use credits.")
    for index, sample in enumerate(s.samples):
        with st.container(border=True):
            st.write(sample["name"])
            show_record(sample)
    st.text_area("Evaluation notes: tone, pitch, timbre, accent, language and pacing", key="observations")

with chat:
    automatic = st.toggle("Automatically generate speech", value=True)
    if st.button("Clear conversation"):
        s.history = []
    if not selected:
        st.info("Start the Ollama application or run ollama serve in a terminal. Run ollama list to check installed models, then refresh connections.")
    message = st.chat_input("Type a message to your robot", disabled=not selected, max_chars=MAX_CHARS)
    if message and selected:
        add_message(s.history, "user", message)
        try:
            with st.spinner("Waiting for the local model..."):
                reply = generate_response(config.ollama_host, selected, s.history, personality, s.tone)
            item = add_message(s.history, "assistant", reply)
            item["configuration"] = metadata
            if automatic:
                item["recording"] = synthesize(reply, metadata)
        except ConversationError as exc:
            st.error(str(exc))
    for i, item in enumerate(s.history):
        with st.chat_message(item["role"]):
            st.text(item["content"])
            if item["role"] == "assistant":
                if not item.get("recording"):
                    if st.button("Generate / retry audio", key=f"retry_{i}"):
                        item["recording"] = synthesize(item["content"], item["configuration"])
                if item.get("recording"):
                    st.audio(item["recording"]["audio"], format="audio/mp3")

with export:
    st.header("Create your final assignment recording")
    st.caption("Aim for 30–60 seconds. Existing recordings can be downloaded without spending credits again.")
    source = st.radio("Recording source", ["Voice Studio sample", "Robot conversation response", "New custom script"])
    chosen = None
    if source == "Voice Studio sample":
        if s.samples:
            i = st.selectbox("Select saved sample", range(len(s.samples)), format_func=lambda i: f"{i+1}. {s.samples[i]['name']}")
            chosen = s.samples[i]
        else:
            st.info("Save a sample in Voice Studio first.")
    elif source == "Robot conversation response":
        recordings = [item["recording"] for item in s.history if item.get("recording")]
        if recordings:
            i = st.selectbox("Select response", range(len(recordings)), format_func=lambda i: f"{i+1}. {recordings[i]['text'][:65]}")
            chosen = recordings[i]
        else:
            st.info("Generate audio for a robot response first.")
    else:
        script = st.text_area("Final script", max_chars=MAX_CHARS, height=180)
        words = len(script.split())
        estimate = words / (150 * s.speed) * 60
        st.caption(f"Estimated duration: {estimate:.0f} seconds ({words} words). Actual duration varies; word counts are less reliable for languages without spaces.")
        if st.button("Generate Final Recording", type="primary", disabled=not script.strip()):
            result = synthesize(script, metadata)
            if result:
                s.final = result
        chosen = s.final
    if chosen:
        st.subheader("Audio preview")
        show_record(chosen)
        st.download_button("Download MP3", chosen["audio"], "reachy-recording.mp3", "audio/mpeg", on_click="ignore")
    st.download_button("Download Voice Configuration JSON",
                       json.dumps(chosen["configuration"] if chosen else metadata, ensure_ascii=False, indent=2),
                       "reachy-voice-configuration.json", "application/json", on_click="ignore")
