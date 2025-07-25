import gradio as gr
import grpc
import uuid
import os
import json
import re
from datetime import datetime

import generated.multimodal_pb2 as multimodal_pb2
import generated.multimodal_pb2_grpc as multimodal_pb2_grpc
import generated.tts_pb2 as tts_pb2
import generated.tts_pb2_grpc as tts_pb2_grpc

# ========== Setup ==========
HISTORY_DIR = "chat_history"
DOWNLOAD_DIR = "downloads"
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

session_id = str(uuid.uuid4())  # Track current session

def slugify(text, max_length=30):
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s_]+", "_", text)
    return text[:max_length] or "chat"

# ========== gRPC Communication ==========
def analyze_with_context(image, audio, text, chatbot_messages):
    global session_id
    # Step 1: Multimodal
    with grpc.insecure_channel("localhost:50051") as mm_channel:
        mm_stub = multimodal_pb2_grpc.MultimodalServiceStub(mm_channel)
        mm_request = multimodal_pb2.MultimodalRequest(
            session_id=session_id,
            image=image.read() if image else b"",
            audio_path=audio.name if audio else "",
            text=text or ""
        )
        mm_response = mm_stub.Analyze(mm_request)

    # Step 2: TTS
    with grpc.insecure_channel("localhost:50052") as tts_channel:
        tts_stub = tts_pb2_grpc.TTSServiceStub(tts_channel)
        tts_request = tts_pb2.TTSRequest(text_output=mm_response.text_output)
        tts_response = tts_stub.Speak(tts_request)

    # Step 3: Update chat
    user_msg = {"role": "user", "content": text or (audio.name if audio else "[Image provided]")}
    bot_msg = {"role": "assistant", "content": mm_response.text_output}

    chatbot_messages.append(user_msg)
    chatbot_messages.append(bot_msg)

    # Save audio to file for download
    audio_path = os.path.join(DOWNLOAD_DIR, f"{session_id}.wav")
    with open(audio_path, "wb") as f:
        f.write(tts_response.audio)

    return chatbot_messages, audio_path

# ========== Chat Reset and Export ==========
def export_session(chatbot_messages):
    global session_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_base = f"{timestamp}__session_{slugify(chatbot_messages[0]['content']) if chatbot_messages else 'chat'}"

    # Save chat
    chat_file = os.path.join(DOWNLOAD_DIR, f"{filename_base}.json")
    with open(chat_file, "w") as f:
        json.dump(chatbot_messages, f)

    # Save audio
    audio_file = os.path.join(DOWNLOAD_DIR, f"{session_id}.wav")
    audio_exists = os.path.exists(audio_file)

    return chat_file, audio_file if audio_exists else None

def reset_after_confirmation(confirmed, chatbot_messages):
    global session_id
    if confirmed == "yes":
        chat_file, audio_file = export_session(chatbot_messages)
        session_id = str(uuid.uuid4())

        # return (
        #     [],  # chatbot
        #     None, None, "", None,
        #     chat_file, audio_file if audio_file else None,
        #     gr.update(visible=False),
        #     gr.update(visible=False),
        #     gr.update(visible=True)
        # )
        return (
            [],  # chatbot
            None, None, "", None,
            gr.update(value=chat_file, visible=True),
            gr.update(value=audio_file, visible=True) if audio_file else None,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True)
        )

    elif confirmed == "no":
        session_id = str(uuid.uuid4())
        return (
            [], None, None, "", None,
            None, None,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True)
        )
    else:
        return (
            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
            gr.update(visible=False), gr.update(visible=False),
            gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
        )

def confirm_before_reset(chatbot_messages):
    if not chatbot_messages:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
    return gr.update(visible=True), gr.update(visible=True), gr.update(visible=False)

# ========== UI ==========
def launch_ui():
    with gr.Blocks(title="Smart Farm Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("## Smart Farm Assistant\nA multimodal assistant for regenerative agriculture.")

        with gr.Row():
            with gr.Column(scale=3):
                clear_btn = gr.Button("Start New Chat", variant="primary")

                confirm_box = gr.Column(visible=False)
                with confirm_box:
                    gr.Markdown("⚠️ You are about to start a new chat. Would you like to download the previous session before proceeding?")
                    confirm_download = gr.Radio(["yes", "no", "cancel"], label="Download before reset?", interactive=True)
                    confirm_btn = gr.Button("Confirm")

                chatbot = gr.Chatbot(label="Chat", show_label=True, render_markdown=True, type="messages")
                response_audio = gr.Audio(label="Response Audio", interactive=False)
                export_chat_btn = gr.Button("Download Chat & Audio")
                chat_file_output = gr.File(label="Chat Download Link", visible=False)
                audio_file_output = gr.File(label="Audio Download Link", visible=False)




            with gr.Column(scale=2):
                image_input = gr.Image(type="filepath", label="Upload Field Image")
                audio_input = gr.Audio(type="filepath", label="Ask via Voice")
                text_input = gr.Textbox(lines=2, placeholder="Type your question", label="Ask via Text")
                submit_btn = gr.Button("Analyze")

                submit_btn.click(
                    analyze_with_context,
                    inputs=[image_input, audio_input, text_input, chatbot],
                    outputs=[chatbot, response_audio]
                )

                # export_chat_btn.click(
                #     export_session,
                #     inputs=[chatbot],
                #     outputs=[chat_file_output, audio_file_output]
                # )

                export_chat_btn.click(
                lambda chatbot: tuple(
                        gr.update(value=path, visible=True) if path else gr.update(visible=False)
                        for path in export_session(chatbot)
                    ),
                    inputs=[chatbot],
                    outputs=[chat_file_output, audio_file_output]
                )



                clear_btn.click(
                    confirm_before_reset,
                    inputs=[chatbot],
                    outputs=[confirm_box, confirm_download, clear_btn]
                )

                confirm_btn.click(
                    reset_after_confirmation,
                    inputs=[confirm_download, chatbot],
                    outputs=[
                        chatbot, image_input, audio_input, text_input, response_audio,
                        chat_file_output, audio_file_output,
                        confirm_box, confirm_download, clear_btn
                    ]
                )


        gr.Markdown("Built with Python, Ollama, and Gemma 3n")

    demo.launch()
