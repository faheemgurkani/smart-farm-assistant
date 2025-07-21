# Smart Farm Assistant for Regenerative Agriculture

A lightweight, multimodal, **offline-first** AI assistant designed to empower **smallholder farmers** with **actionable agricultural insights**. This assistant utilizes the power of **Gemma 3n** and runs fully locally using **Gradio** for the frontend and **gRPC** for backend communication. It supports **image**, **audio**, and **text** inputs to guide sustainable and regenerative farming practices.

---

## Features

### Multimodal Chat Interface

* Seamlessly supports **image uploads**, **voice queries**, and **text questions**.
* Real-time **chat-based interaction** with contextual memory.

### Image-Based Field Analysis

* Detects:

  * **Dryness**
  * **Unhealthy patches**
  * **Crop residue**
  * **Weed overgrowth**

### Voice Query Understanding

* Handles **voice instructions** for hands-free operation.
* Extracts actionable insights from audio and responds with **optional audio playback**.

### Text Input Support

* Ask farming questions in local or English language.
* Auto-language detection and answer generation.

### Chat History Management

* **Auto-saves** every session.
* **Auto-renames** session files based on the first user message.
* Load past sessions via dropdown selector.

---

## Tech Stack

| Component | Technology                                                                     |
| --------- | ------------------------------------------------------------------------------ |
| Backend   | Python, gRPC, Protobuf                                                         |
| Frontend  | Gradio (Blocks API)                                                            |
| Models    | Local AI via Ollama, Gemma 3n (text), whisper/jina (ASR), vision model (image) |

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smart-farm-assistant.git
cd smart-farm-assistant
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Backend gRPC Server

```bash
python server.py
```

### 4. Launch Gradio Frontend

```bash
python app.py
```

---

## Use-Cases

| Use-Case           | Description                                                                            |
| ------------------ | -------------------------------------------------------------------------------------- |
| Field Monitoring   | Upload an image of your farmland to receive insights on soil, crop health, weeds, etc. |
| Voice-Based Help   | Ask queries via microphone (e.g., "What to do if soil is dry?")                        |
| Multilingual Query | Enter questions in different languages, the assistant will respond accordingly.        |
| Session Recall     | Revisit earlier advice and responses via chat history loading.                         |

---

## Project Structure

```
smart-farm-assistant/
├── app.py                # Gradio-based UI frontend
├── server.py             # gRPC server backend
├── generated/            # Protobuf generated files
├── protos/               # .proto definitions
├── chat_history/         # Auto-saved chat logs
├── requirements.txt
└── README.md
```

---

## Future Enhancements

* Offline speech-to-text and TTS using faster whisper models
* Multilingual UI & regional crop database
* Soil sensor data integration
* RAG-based document retrieval from agricultural policies

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

* [Ollama](https://ollama.com/) for local LLMs
* [Gemma 3n](https://ai.google.dev/gemma) for multilingual reasoning
* [Gradio](https://www.gradio.app/) for the seamless interface
* [FAO](https://www.fao.org/) for inspiration in regenerative agriculture

---

## Feedback & Contributions

We welcome PRs, suggestions, and issues! Together, let's empower sustainable agriculture through AI.

---

> Built by Muhammad Faheem for the Gemma 3n Hackathon

