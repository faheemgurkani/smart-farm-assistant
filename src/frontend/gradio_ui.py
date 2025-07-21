import gradio as gr
import grpc
import uuid
import os
import json
import re
from datetime import datetime

import generated.farm_pb2 as farm_pb2
import generated.farm_pb2_grpc as farm_pb2_grpc

# ========== Chat History Persistence Setup ==========
HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

session_id = str(uuid.uuid4())  # Track current session


def slugify(text, max_length=30):
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s_]+", "_", text)
    return text[:max_length] or "chat"


def save_chat_session(session_id, messages):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
    safe_summary = slugify(first_user_msg)
    filename = f"{timestamp}__{safe_summary}.json"
    filepath = os.path.join(HISTORY_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(messages, f)


def list_past_sessions():
    files = [f for f in sorted(os.listdir(HISTORY_DIR), reverse=True) if f.endswith(".json")]
    sessions = []
    for f in files:
        try:
            timestamp, summary = f.replace(".json", "").split("__", 1)
            readable_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M")
            label = f"{readable_time} - {summary.replace('_', ' ').capitalize()}"
        except:
            label = f
        sessions.append((label, f))
    return sessions


def load_chat_session(file):
    if not file:
        return []
    try:
        with open(os.path.join(HISTORY_DIR, file), "r") as f:
            return json.load(f)
    except:
        return []


def delete_chat_session(file):
    try:
        os.remove(os.path.join(HISTORY_DIR, file))
    except:
        pass
    return gr.update(choices=list_past_sessions(), value=None)


# ========== Core Chat Functionality ==========
def analyze_with_context(image, audio, text, chatbot_messages):
    global session_id
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = farm_pb2_grpc.FarmingStub(channel)
        request = farm_pb2.FarmRequest(
            session_id=session_id,
            image=image.read() if image else b"",
            audio=audio.name if audio else "",
            text=text or ""
        )
        response = stub.Analyze(request)

        user_message = {
            "role": "user",
            "content": text or (audio.name if audio else "[Image provided]")
        }
        assistant_message = {
            "role": "assistant",
            "content": response.advice
        }

        chatbot_messages.append(user_message)
        chatbot_messages.append(assistant_message)
        return chatbot_messages, response.audio


def reset_chat(chatbot_messages):
    global session_id
    save_chat_session(session_id, chatbot_messages)
    session_id = str(uuid.uuid4())
    return [], None, None, "", gr.update(choices=list_past_sessions(), value=None)


# ========== UI Launch ==========
def launch_ui():
    with gr.Blocks(title="Smart Farm Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("## 🌾 Smart Farm Assistant\nA multimodal assistant for regenerative agriculture.")

        with gr.Row():
            with gr.Column(scale=3):
                with gr.Row():
                    clear_btn = gr.Button("Start New Chat")

                # Modern dropdown + stacked buttons
                session_selector = gr.Dropdown(
                    choices=list_past_sessions(),
                    label="📁 Load Past Chat",
                    interactive=True,
                    allow_custom_value=False,
                )
                load_button = gr.Button("Load", interactive=False)
                delete_button = gr.Button("🗑️ Delete", variant="stop", interactive=False)

                # Enable buttons only when a session is selected
                session_selector.change(
                    lambda val: (
                        gr.update(interactive=bool(val)),
                        gr.update(interactive=bool(val)),
                    ),
                    inputs=session_selector,
                    outputs=[load_button, delete_button],
                )

                chatbot = gr.Chatbot(label="Chat History", show_label=True, render_markdown=True, type="messages")
                response_audio = gr.Audio(label="Response Audio")

            with gr.Column(scale=2):
                image_input = gr.Image(type="filepath", label="Upload Field Image")
                audio_input = gr.Audio(type="filepath", label="Ask via Voice")
                text_input = gr.Textbox(lines=2, placeholder="Type your question", label="Ask via Text")
                submit_btn = gr.Button("🔍 Analyze")

                submit_btn.click(
                    analyze_with_context,
                    inputs=[image_input, audio_input, text_input, chatbot],
                    outputs=[chatbot, response_audio]
                )

                clear_btn.click(
                    reset_chat,
                    inputs=[chatbot],
                    outputs=[chatbot, image_input, audio_input, text_input, session_selector]
                )

                load_button.click(
                    load_chat_session,
                    inputs=session_selector,
                    outputs=chatbot
                )

                delete_button.click(
                    delete_chat_session,
                    inputs=session_selector,
                    outputs=session_selector
                )

        gr.Markdown("Built with 🐍 Python, 🤖 Ollama, and 🌿 Gemma 3n")

    demo.launch()
