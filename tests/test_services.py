from unittest.mock import Mock, patch
import pytest
from voice import Settings, VoiceError, generate_audio
from conversation import Personality, ConversationError, generate_response, check_server, add_message

def test_speech_sdk():
    with patch("voice.ElevenLabs") as factory:
        convert = factory.return_value.text_to_speech.convert
        convert.return_value = iter([b"ID3", b"audio"])
        assert generate_audio("Hello", "mock-key", "voice", Settings()) == b"ID3audio"
        kwargs = convert.call_args.kwargs
        assert kwargs["output_format"] == "mp3_44100_128"
        assert kwargs["request_options"] == {"max_retries": 0}
        assert "language_code" not in kwargs
        assert kwargs["voice_settings"].speed == 1.0
        assert convert.call_count == 1

@pytest.mark.parametrize("status,expected", [(401,"authentication"), (404,"Voice ID"), (402,"credits"), (429,"rate limit"), (422,"rejected"), (None,"connection")])
def test_safe_errors(status, expected):
    with patch("voice.ElevenLabs") as factory:
        failure = Exception("secret-key")
        failure.status_code = status
        convert = factory.return_value.text_to_speech.convert
        convert.side_effect = failure
        with pytest.raises(VoiceError, match=expected) as error:
            generate_audio("Hello", "secret-key", "voice", Settings())
        assert "secret-key" not in str(error.value)
        assert convert.call_count == 1

def test_missing_and_length():
    with patch("voice.ElevenLabs") as factory:
        for text, key in [("hi", ""), ("x"*1501, "key"), (" ", "key")]:
            with pytest.raises(VoiceError):
                generate_audio(text, key, "voice", Settings())
        factory.assert_not_called()

def test_local_conversation():
    with patch("conversation.ollama.Client") as factory:
        client = factory.return_value
        client.list.return_value.models = [Mock(model="local:latest", remote_host=None)]
        assert check_server("http://localhost:11434") == (True, ["local:latest"])
        history = []
        add_message(history, "user", "Hello")
        client.chat.return_value.message.content = "Welcome!"
        assert generate_response("http://localhost:11434", "local:latest", history, Personality(language="French"), "Calm") == "Welcome!"
        messages = client.chat.call_args.kwargs["messages"]
        assert "French" in messages[0]["content"] and "Calm" in messages[0]["content"]
        assert messages[1] == history[0]
        client.chat.return_value.message.content = ""
        with pytest.raises(ConversationError, match="no text"):
            generate_response("http://localhost:11434", "local:latest", history, Personality())
        client.list.side_effect = ConnectionError()
        assert check_server("http://localhost:11434") == (False, [])
