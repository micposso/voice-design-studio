from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from config import Config
from voice import VoiceError

APP = str(Path(__file__).resolve().parents[1] / "app.py")
def button(at, label):
    return next(x for x in at.button if x.label == label)

def test_voice_independent_and_rerun_safe():
    with patch("config.load_config", return_value=Config("mock-key", "mock-voice", "", "http://localhost:11434")), patch("conversation.check_server", return_value=(False, [])), patch("voice.generate_audio", return_value=b"ID3mock") as speech:
        at = AppTest.from_file(APP).run()
        assert not at.exception
        speech.assert_not_called()
        for _ in range(3):
            button(at, "Generate Voice").click().run()
            button(at, "Save Sample").click().run()
        assert len(at.session_state.samples) == 3
        assert speech.call_count == 3
        assert at.session_state.samples[0]["audio"] == b"ID3mock"
        at.slider(key="speed").set_value(1.2).run()
        assert speech.call_count == 3
        assert at.session_state.samples[0]["configuration"]["voice_settings"]["speed"] == 1.0
        assert any(x.proto.label == "Download MP3" for x in at.get("download_button"))
        button(at, "Refresh connections").click().run()
        assert speech.call_count == 3
        assert not at.exception

def test_chat_audio_retry_and_export():
    with patch("config.load_config", return_value=Config("mock-key", "mock-voice", "local", "http://localhost:11434")), patch("conversation.check_server", return_value=(True, ["local"])), patch("conversation.generate_response", return_value="Welcome!") as chat, patch("voice.generate_audio", side_effect=[VoiceError("Try again"), b"ID3mock"]) as speech:
        at = AppTest.from_file(APP).run()
        at.chat_input[0].set_value("Hello").run()
        assert chat.call_count == 1 and speech.call_count == 1
        assert at.session_state.history[-1]["content"] == "Welcome!"
        at.run()
        assert speech.call_count == 1
        button(at, "Generate / retry audio").click().run()
        assert speech.call_count == 2
        at.radio[0].set_value("Robot conversation response").run()
        assert any(x.proto.label == "Download MP3" for x in at.get("download_button"))
        assert speech.call_count == 2
        assert not at.exception

def test_missing_credentials():
    with patch("config.load_config", return_value=Config("", "", "", "http://localhost:11434")), patch("conversation.check_server", return_value=(False, [])):
        at = AppTest.from_file(APP).run()
        button(at, "Generate Voice").click().run()
        assert any("Add your ElevenLabs" in x.value for x in at.error)
        assert not at.exception

def test_new_final_recording_and_reset():
    with patch("config.load_config", return_value=Config("mock-key", "mock-voice", "", "http://localhost:11434")), patch("conversation.check_server", return_value=(False, [])), patch("voice.generate_audio", return_value=b"ID3final") as speech:
        at = AppTest.from_file(APP).run()
        at.slider(key="speed").set_value(1.2).run()
        at.radio[0].set_value("New custom script").run()
        next(x for x in at.text_area if x.label == "Final script").set_value("Welcome to the laboratory.").run()
        button(at, "Generate Final Recording").click().run()
        assert at.session_state.final["audio"] == b"ID3final"
        assert at.session_state.final["configuration"]["voice_settings"]["speed"] == 1.2
        assert "mock-key" not in str(at.session_state.final["configuration"])
        assert any(x.proto.label == "Download MP3" for x in at.get("download_button"))
        button(at, "Reset Settings").click().run()
        assert at.session_state.speed == 1.0
        assert speech.call_count == 1
        assert not at.exception
