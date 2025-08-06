import requests
import base64

def generate_response(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "gemma3n:e4b",  # adjust to whatever you're using
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print(f"Error from Ollama: {response.status_code}, {response.text}")
            return ""
    except Exception as e:
        print("Exception while connecting to Ollama:", e)
        return ""

def generate_vision_response(prompt: str, image_bytes: bytes) -> str:
    """Generate response from vision model with image input"""
    url = "http://localhost:11434/api/generate"
    
    # First, let's check if the model supports vision
    try:
        model_info_url = "http://localhost:11434/api/show"
        model_info_response = requests.post(model_info_url, json={"name": "gemma3n:e4b"})
        if model_info_response.status_code == 200:
            model_info = model_info_response.json()
            print(f"[OLLAMA] Model info: {model_info.get('modelfile', '')[:200]}...")
        else:
            print(f"[OLLAMA] Could not get model info: {model_info_response.status_code}")
    except Exception as e:
        print(f"[OLLAMA] Error getting model info: {e}")
    
    # Encode image to base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Try different payload formats for vision models
    payload_formats = [
        # Format 1: Standard vision format
        {
            "model": "gemma3n:e4b",
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        },
        # Format 2: Alternative format with image_data
        {
            "model": "gemma3n:e4b",
            "prompt": prompt,
            "image_data": [image_base64],
            "stream": False
        },
        # Format 3: Single image format
        {
            "model": "gemma3n:e4b",
            "prompt": prompt,
            "image": image_base64,
            "stream": False
        }
    ]
    
    print(f"[OLLAMA] Sending vision request to {url}")
    print(f"[OLLAMA] Model: gemma3n:e4b")
    print(f"[OLLAMA] Prompt length: {len(prompt)}")
    print(f"[OLLAMA] Image base64 length: {len(image_base64)}")
    
    for i, payload in enumerate(payload_formats, 1):
        print(f"[OLLAMA] Trying payload format {i}: {list(payload.keys())}")
        
        try:
            response = requests.post(url, json=payload)
            print(f"[OLLAMA] Response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[OLLAMA] Response keys: {list(response_data.keys())}")
                response_text = response_data.get("response", "").strip()
                
                # Debug: Print first 200 characters of response
                print(f"[OLLAMA] Response preview: {response_text[:200]}...")
                
                # Check if the response actually analyzes the image or asks for it
                if "provide the image" in response_text.lower() or "awaiting the image" in response_text.lower():
                    print(f"[OLLAMA] Format {i} failed - model asking for image")
                    continue
                else:
                    print(f"[OLLAMA] Format {i} succeeded - model analyzed image")
                    return response_text
            else:
                print(f"Error from Ollama vision API (format {i}): {response.status_code}, {response.text}")
                
        except Exception as e:
            print(f"Exception while connecting to Ollama vision API (format {i}): {e}")
    
    # If all formats fail, return a fallback response
    print("[OLLAMA] All vision formats failed, using fallback")
    return "I'm having trouble analyzing the image. Please try uploading a clearer image or contact support."
