# run_all.py
import subprocess
import time



def launch_services():
    # Launch MultimodalService
    mm_proc = subprocess.Popen(["python3", "scripts/run_multimodal_server.py"])
    time.sleep(1)  # Optional: Give time to start

    print()

    # Launch TTSService
    tts_proc = subprocess.Popen(["python3", "scripts/run_tts_server.py"])
    time.sleep(1)
    
    # print()

    # Launch Gradio UI
    ui_proc = subprocess.Popen(["python3", "scripts/run_ui.py"])

    # print()

    try:
        ui_proc.wait()
    except KeyboardInterrupt:
        print("Shutting down all services...")

    mm_proc.terminate()
    tts_proc.terminate()
    ui_proc.terminate()

if __name__ == "__main__":
    launch_services()
