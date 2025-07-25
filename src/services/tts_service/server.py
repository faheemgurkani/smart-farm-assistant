import grpc
from concurrent import futures

from generated import tts_pb2, tts_pb2_grpc
from src.services.tts_service import tts


class TTSServiceServicer(tts_pb2_grpc.TTSServiceServicer):
    def Speak(self, request, context):
        text_output = request.text_output
        audio_bytes = tts.speak(text_output)
        return tts_pb2.TTSResponse(audio=audio_bytes)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tts_pb2_grpc.add_TTSServiceServicer_to_server(TTSServiceServicer(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("TTSService gRPC server started on port 50052.")
    server.wait_for_termination()
