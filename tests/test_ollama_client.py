import sys
import os

# Adding the project root (the directory containing 'src' and 'scripts') to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)


from src.server.ollama_client import generate_response

prompt = "What are the best practices for planting tomatoes in July?"
response = generate_response(prompt)
print("LLM response:", response)
