import grpc
from concurrent import futures
import time
import generated.farm_pb2 as farm_pb2
import generated.farm_pb2_grpc as farm_pb2_grpc

from src.server import ollama_client, tts, vision, asr, logger
from src.server import chat_memory
from src.utils.prompt_builder import build_prompt

# class FarmingServicer(farm_pb2_grpc.FarmingServicer):
#     def Analyze(self, request, context):
#         image_prompt = vision.process_image(request.image) if request.image else ""
#         audio_text = asr.transcribe(request.audio) if request.audio else ""
#         prompt = build_prompt(request.text, image_prompt, audio_text)
        
#         advice = ollama_client.generate_response(prompt)
#         audio_bytes = tts.speak(advice)

#         logger.log_entry("mixed", prompt, advice, audio_path=None)  # simplified

#         return farm_pb2.FarmReply(advice=advice, audio=audio_bytes)

class FarmingServicer(farm_pb2_grpc.FarmingServicer):
    def Analyze(self, request, context):
        image_prompt = vision.process_image(request.image) if request.image else ""
        audio_text = asr.transcribe(request.audio) if request.audio else ""
        session_id = request.session_id or "default"

        # Append previous context
        prev_messages = chat_memory.get_history(session_id)
        prev_context = "\n".join([f"{m['role']}: {m['message']}" for m in prev_messages])
        
        prompt = build_prompt(request.text, image_prompt, audio_text)
        full_prompt = (prev_context + "\nUser: " + prompt).strip()

        advice = ollama_client.generate_response(full_prompt)
        audio_bytes = tts.speak(advice)

        chat_memory.add_message(session_id, "User", prompt)
        chat_memory.add_message(session_id, "Assistant", advice)

        logger.log_entry("mixed", prompt, advice)

        return farm_pb2.FarmReply(advice=advice, audio=audio_bytes)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    farm_pb2_grpc.add_FarmingServicer_to_server(FarmingServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server started on port 50051.")
    server.wait_for_termination()
