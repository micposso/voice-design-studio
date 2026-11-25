# Reachy Voice Lab

**ARTI 609 — Designing Voice Experiences for Social Robots**  
New York Institute of Technology

A 90-minute graduate UX/design workshop. Explore your custom voice, design a robot personality, chat with a local AI model and export a final recording. No robot hardware is required.

## Before class

Install Git, VS Code, [Ollama](https://ollama.com/download), and uv. Have an ElevenLabs account with a custom voice, API access and sufficient credits. Ollama inference is local; speech synthesis sends your script to ElevenLabs over the internet. Only use voices and content you have permission to use.

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS (Terminal)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal after installing uv. The remaining commands are identical on Windows and macOS:

```text
uv --version
uv python install 3.12
git clone YOUR_REPOSITORY_URL
cd reachy-voice-lab
uv sync
uv run python --version
ollama list
```

Replace YOUR_REPOSITORY_URL with the repository URL supplied by your instructor. If you already have the project folder, skip cloning and open that folder instead. Python should report 3.12.x. uv manages the virtual environment; you do not need to activate it or use pip.

Start the Ollama desktop application. If needed, run `ollama serve` in a separate terminal. Run `ollama list` to see installed models. If the list is empty, ask your instructor which model to install, then run `ollama pull MODEL_NAME` using the assigned name. The lab never downloads models automatically. Choose a locally installed, non-cloud model.

## Configure your voice

1. Open the project folder in VS Code.
2. In the Explorer, copy the contents of .env.example into a new file named exactly .env (not .env.txt).
3. In ElevenLabs, open your account's API keys page and create or copy a key with text-to-speech access. Paste it after ELEVENLABS_API_KEY=.
4. In the ElevenLabs Voices area, locate your custom voice and copy its Voice ID from its details or menu. Paste it after ELEVENLABS_VOICE_ID=.
5. Set OLLAMA_MODEL to an exact installed model name from ollama list, or leave it blank to choose in the app. Leave OLLAMA_HOST at its local default.

Never share your .env file, key, or screenshots showing the key. Only .env.example belongs in Git.

## Launch

```text
uv run streamlit run app.py
```

Open http://localhost:8501 in your browser. Stop the application with Ctrl+C in the terminal.

## 90-minute workshop

| Time | Activity |
|---|---|
| 0–15 min | Set up, launch, check sidebar configuration |
| 15–40 min | Voice Studio: generate and save at least three distinct samples |
| 40–65 min | AI Conversation: configure personality and complete three exchanges |
| 65–85 min | Export MP3: write a final script, generate, listen and download |
| 85–90 min | Reflect and submit |

### Assignment: a social robot laboratory assistant

Design a voice and personality for a social robot working as a university robotics laboratory assistant.

1. Generate and compare at least three saved voice samples; vary one setting at a time.
2. Evaluate tone, pitch, timbre, accent, language, and rhythm/pacing. Record observations in Voice Studio.
3. Complete at least three conversational exchanges with the local AI assistant.
4. Generate a final 30–60-second MP3. At normal speed, try about 75–150 words, then listen and adjust as needed.
5. Write a short paragraph explaining your voice design decisions: what changed, why, and how the voice supports the robot's role.

Submit the MP3, voice configuration JSON and reflection using your instructor's submission instructions. Keep notes and downloaded files before closing the browser: session recordings, history and observations are temporary. Put downloaded files in outputs if desired; the app does not automatically write audio to disk.

### Voice Studio

Tone changes the suggested dialogue and local AI personality instructions. Pitch, timbre and accent are primarily properties of the original voice. Speed controls the delivery rate, stability controls consistency, similarity boost controls resemblance to the voice, style exaggeration emphasizes its characteristics, and speaker boost enhances voice similarity. Language selection does not translate text; Multilingual v2 detects language from the text itself. Write the script in your intended language.

Generate Voice is an explicit paid request. Saving, replaying, changing controls and exporting previously generated audio do not make new speech requests. The settings shown alongside audio reflect the original generation, not the latest sliders.

### AI Conversation

Select a local Ollama model in the sidebar and customize your robot. Submit typed messages. Automatic speech can be disabled to conserve credits; generate audio for individual responses when needed. A failed speech request leaves its text available for manual retry.

### Export MP3

Choose an existing recording or write a new script. The duration estimate uses 150 words per minute adjusted by speed; actual speech and languages without word spaces can differ. Download the MP3 and JSON, which contains the voice ID and design configuration, but no API key. Existing recordings retain the configuration used to create them.

## Troubleshooting

| Issue | Try this |
|---|---|
| Windows: uv not recognized | Restart PowerShell and VS Code; confirm uv installation completed. Use the exact installer command above. |
| macOS: uv not recognized | Restart Terminal; follow the installer PATH instructions. If using Apple Silicon, use a native terminal. |
| uv sync fails | Check internet access and package index availability; rerun uv sync. Verify Python 3.12 is installed. |
| Ollama unavailable | Open Ollama or run ollama serve; check ollama list and refresh the sidebar. A port-in-use message can mean Ollama is already running. |
| No model or missing model | Install the instructor-approved model manually, refresh and select it. |
| Ollama slow / timeout | Try a smaller installed model and close memory-intensive applications. |
| ElevenLabs key missing or rejected | Check .env spelling, key permissions and account access; restart Streamlit after edits. |
| Voice ID invalid | Copy the ID from your custom voice, not its display name. |
| Credits or rate limit | Check your balance and plan; wait before trying again. The app never automatically retries paid speech requests. |
| Audio playback | Press play manually; check volume, browser output device, and try a current browser. Download the MP3 to play it locally. |

## Architecture and testing

- app.py: native Streamlit UI, session state, recording metadata and downloads.
- config.py: .env loading and shared defaults.
- voice.py: reusable ElevenLabs generation function returning MP3 bytes.
- conversation.py: local Ollama model discovery, personality and text generation.
- tests/: mocked SDK and Streamlit state tests.
- outputs/: optional location for student downloads (ignored by Git).

Run the tests without paid requests:

```text
uv run pytest
uv run python -m compileall app.py config.py voice.py conversation.py tests
```

For the next class, reuse the Python modules in a Reachy Mini application: obtain the robot personality, generate local text using conversation.py, then synthesize bytes via voice.py and pass them to a future playback adapter. No Reachy Mini SDK, microphone, streaming speech, Docker, Node.js or audio conversion tools are required in this version.

## Official documentation

- [ElevenLabs speech endpoint](https://elevenlabs.io/docs/api-reference/text-to-speech/convert)
- [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python)
- [Ollama Python SDK](https://github.com/ollama/ollama-python)
- [Streamlit app testing](https://docs.streamlit.io/develop/concepts/app-testing)
- [Streamlit downloads](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button)
- [uv project syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
