"""Local conversation and personality logic; no Streamlit dependency."""
from dataclasses import dataclass
import ollama

DEFAULT_PROMPT = "You are Reachy, a friendly social robot working as an assistant in a university robotics laboratory. Your purpose is to welcome visitors, answer questions, explain robotics concepts and help students navigate the laboratory. Communicate clearly, naturally and respectfully. Keep responses concise, conversational and suitable for spoken delivery. Do not use markdown formatting, emojis or unnecessary special characters. Do not claim to perform physical actions or perceive the environment."

class ConversationError(Exception):
    pass

@dataclass(frozen=True)
class Personality:
    name: str = "Reachy"
    role: str = "University robotics laboratory assistant."
    personality: str = "Friendly, curious and helpful"
    style: str = "Clear and conversational"
    language: str = "English"
    instructions: str = ""

    def system_prompt(self, tone="Friendly"):
        return (f"{DEFAULT_PROMPT}\nUse the following customization instead of any conflicting default name or role: "
                f"Name: {self.name}. Role: {self.role}. Personality: {self.personality}. "
                f"Communication style: {self.style}. Tone: {tone}. Respond in {self.language}. "
                f"Additional instructions: {self.instructions or 'None'}. "
                "Keep each answer to two or three short sentences, plain spoken text only.")

def installed_models(host):
    try:
        response = ollama.Client(host=host, timeout=4).list()
        return sorted(m.model for m in response.models if m.model)
    except Exception:
        raise ConversationError("Ollama is unavailable. Start Ollama and click Refresh connections.") from None

def check_server(host):
    try:
        return True, installed_models(host)
    except ConversationError:
        return False, []

def generate_response(host, model, history, personality, tone="Friendly"):
    if not model:
        raise ConversationError("Select an installed Ollama model first.")
    try:
        messages = [{"role": "system", "content": personality.system_prompt(tone)}]
        messages += [{"role": item["role"], "content": item["content"]} for item in history]
        result = ollama.Client(host=host, timeout=120).chat(
            model=model, messages=messages, stream=False, options={"num_predict": 160})
        answer = (result.message.content or "").strip()
        if not answer:
            raise ConversationError("The model returned no text. Try another message or model.")
        return answer
    except ConversationError:
        raise
    except ollama.ResponseError as exc:
        if exc.status_code == 404:
            raise ConversationError("Model not found. Refresh connections and select an installed model.") from None
        raise ConversationError("Ollama could not generate a response. Check the local model.") from None
    except Exception:
        raise ConversationError("Ollama did not respond. Check that it is running; the model may need more time or memory.") from None

def add_message(history, role, content):
    history.append({"role": role, "content": content})
    return history[-1]
