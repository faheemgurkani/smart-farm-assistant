import sys, os

# Adding the project root (the directory containing 'src' and 'scripts') to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.multimodal_service import server, ollama_startup

if __name__ == "__main__":
    ollama_startup.start_ollama()
    server.serve()

