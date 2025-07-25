import sys, os

# Adding the project root (the directory containing 'src' and 'scripts') to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.tts_service import server

if __name__ == "__main__":
    server.serve()
