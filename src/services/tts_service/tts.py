import pyttsx3
import tempfile

engine = pyttsx3.init()

def speak(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        engine.save_to_file(text, fp.name)
        engine.runAndWait()
        return fp.read()
