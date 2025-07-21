import sys
import os

# Adding the project root (the directory containing 'src' and 'scripts') to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.server import grpc_server, ollama_startup

ollama_startup.start_ollama()
grpc_server.serve()
