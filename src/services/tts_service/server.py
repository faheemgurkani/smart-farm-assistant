import grpc
from concurrent import futures
import logging

from generated import tts_pb2, tts_pb2_grpc
from src.services.tts_service import tts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSServiceServicer(tts_pb2_grpc.TTSServiceServicer):
    def Speak(self, request, context):
        """Convert text to speech"""
        try:
            text_output = request.text_output
            output_format = getattr(request, 'output_format', 'wav')
            language_code = getattr(request, 'language_code', None)
            
            logger.info(f"TTS request: {len(text_output)} characters, format: {output_format}, language: {language_code}")
            
            audio_bytes = tts.speak(text_output, output_format, language_code)
            
            if audio_bytes:
                logger.info(f"TTS generated {len(audio_bytes)} bytes of audio")
                return tts_pb2.TTSResponse(audio=audio_bytes)
            else:
                logger.error("TTS failed to generate audio")
                return tts_pb2.TTSResponse(audio=b"")
                
        except Exception as e:
            logger.error(f"TTS service error: {e}")
            return tts_pb2.TTSResponse(audio=b"")
    
    def GetStatus(self, request, context):
        """Get TTS service status"""
        try:
            status = tts.get_tts_status()
            return tts_pb2.TTSStatusResponse(
                coqui_available=status["coqui_available"],
                model_loaded=status["model_loaded"],
                fallback_available=status["fallback_available"],
                available_models=", ".join(status["available_models"])
            )
        except Exception as e:
            logger.error(f"Status request error: {e}")
            return tts_pb2.TTSStatusResponse(
                coqui_available=False,
                model_loaded=False,
                fallback_available=False,
                available_models=""
            )

def serve():
    """Start the TTS gRPC server"""
    # Configure server with larger message size limits
    server_options = [
        ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB send limit
        ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB receive limit
    ]
    
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=server_options
    )
    tts_pb2_grpc.add_TTSServiceServicer_to_server(TTSServiceServicer(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    logger.info("Enhanced TTS Service gRPC server started on port 50052.")
    logger.info("Features: Coqui TTS with pyttsx3 fallback")
    logger.info("Message size limits: 50MB send/receive")
    server.wait_for_termination()
