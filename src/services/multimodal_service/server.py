import grpc
from concurrent import futures

from generated import multimodal_pb2, multimodal_pb2_grpc

from src.services.multimodal_service import ollama_client, vision, asr, chat_memory
from src.utils.prompt_builder import build_prompt
from src.db import logger


class MultimodalServicer(multimodal_pb2_grpc.MultimodalServiceServicer):
    def Analyze(self, request, context):
        session_id = request.session_id or "default"

        # Process image and audio
        image_prompt = vision.process_image(request.image) if request.image else ""
        audio_text = asr.transcribe(request.audio_path) if request.audio_path else ""

        # Get prior messages for context
        prev_messages = chat_memory.get_history(session_id)
        prev_context = "\n".join([f"{m['role']}: {m['message']}" for m in prev_messages])

        # Construct prompt
        user_prompt = build_prompt(request.text, image_prompt, audio_text)
        full_prompt = (prev_context + "\nUser: " + user_prompt).strip()

        # Generate response via LLM
        text_output = ollama_client.generate_response(full_prompt)

        # Update session memory + logs
        chat_memory.add_message(session_id, "User", user_prompt)
        chat_memory.add_message(session_id, "Assistant", text_output)
        logger.log_entry("mixed", user_prompt, text_output)

        return multimodal_pb2.MultimodalResponse(text_output=text_output)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    multimodal_pb2_grpc.add_MultimodalServiceServicer_to_server(MultimodalServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("MultimodalService gRPC server started on port 50051.")
    server.wait_for_termination()
