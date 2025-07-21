import subprocess, socket, time, atexit

ollama_proc = None

def is_ollama_running(host="127.0.0.1", port=11434):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except:
        return False

def start_ollama():
    global ollama_proc
    if not is_ollama_running():
        print("Starting Ollama...")
        ollama_proc = subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL)
        time.sleep(2)

def stop_ollama():
    global ollama_proc
    if ollama_proc:
        ollama_proc.terminate()

atexit.register(stop_ollama)
