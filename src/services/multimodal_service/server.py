import grpc
from concurrent import futures
import numpy as np
import json
import os
from typing import List, Dict, Any

from generated import multimodal_pb2, multimodal_pb2_grpc

from src.services.multimodal_service import ollama_client, vision, asr, chat_memory, session_manager
from src.services.language_detection import language_detector
from src.utils.prompt_builder import build_prompt
from src.services.multimodal_service.chat_memory import get_context, update_context
from src.services.multimodal_service.session_manager import session_manager
from db import logger

# --- RAG-based FAQ Worker Implementation ---
class SimpleVectorDB:
    """Simple in-memory vector database for demo purposes"""
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.doc_ids = []
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add documents and their embeddings to the vector DB"""
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)
        self.doc_ids.extend([f"doc_{i}" for i in range(len(documents))])
    
    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for most similar documents using cosine similarity"""
        if not self.embeddings:
            return []
        
        # Calculate cosine similarities
        similarities = []
        for doc_embedding in self.embeddings:
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append(similarity)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'id': self.doc_ids[idx],
                'content': self.documents[idx]['content'],
                'title': self.documents[idx].get('title', ''),
                'similarity': similarities[idx]
            })
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

class SimpleEmbeddingModel:
    """Simple embedding model for demo purposes"""
    def __init__(self):
        # Dummy embedding dimensions
        self.embedding_dim = 384
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text (dummy implementation)"""
        # In a real implementation, you would use a proper embedding model
        # For now, we'll create a simple hash-based embedding
        import hashlib
        
        # Create a hash of the text
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert hash to embedding-like vector
        embedding = []
        for i in range(0, min(len(hash_bytes), self.embedding_dim // 4)):
            # Use 4 bytes to create a float
            float_val = int.from_bytes(hash_bytes[i:i+4], byteorder='big') / (2**32)
            embedding.append(float_val)
        
        # Pad or truncate to embedding_dim
        while len(embedding) < self.embedding_dim:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dim]

# Initialize RAG components
embedding_model = SimpleEmbeddingModel()
vector_db = SimpleVectorDB()

# Dummy knowledge base data
def initialize_knowledge_base():
    """Initialize the knowledge base with dummy agricultural FAQ data"""
    knowledge_base = [
        {
            "title": "Wheat Planting Guide",
            "content": "Wheat should be planted in November for best results in Punjab. The optimal soil pH is 6.5-7.5. Plant seeds 1-2 inches deep and 6-8 inches apart. Water regularly but avoid waterlogging."
        },
        {
            "title": "Cabbage Pest Control",
            "content": "Cabbage is susceptible to cabbage white butterfly larvae. Use row covers to prevent egg laying. Apply Bacillus thuringiensis (Bt) for organic control. Handpick caterpillars in early morning."
        },
        {
            "title": "Soil pH Testing",
            "content": "Test soil pH using a pH meter or test kit. Most crops prefer pH 6.0-7.0. Add lime to raise pH or sulfur to lower pH. Test soil every 2-3 years for optimal results."
        },
        {
            "title": "NPK Fertilizer Application",
            "content": "NPK fertilizer contains Nitrogen (N), Phosphorus (P), and Potassium (K). Apply 100-150 kg per hectare for wheat. Split application: 50% at planting, 50% at tillering stage."
        },
        {
            "title": "Organic Fertilizers",
            "content": "Organic fertilizers include compost, manure, and vermicompost. Apply 5-10 tonnes per hectare. They improve soil structure and provide slow-release nutrients. Mix well with soil before planting."
        },
        {
            "title": "Irrigation Best Practices",
            "content": "Water crops early morning to reduce evaporation. Use drip irrigation for water efficiency. Monitor soil moisture with a moisture meter. Avoid overwatering which can cause root rot."
        },
        {
            "title": "Crop Rotation Benefits",
            "content": "Crop rotation prevents soil depletion and pest buildup. Rotate between legumes (fix nitrogen) and grains (use nitrogen). Plan 3-4 year rotation cycles for best results."
        },
        {
            "title": "Pest Identification",
            "content": "Common pests include aphids, caterpillars, and beetles. Look for chewed leaves, holes, or yellowing. Use integrated pest management: cultural, biological, and chemical controls."
        },
        {
            "title": "Soil Compaction Solutions",
            "content": "Soil compaction reduces root growth and water infiltration. Use deep tillage to break compacted layers. Add organic matter to improve soil structure. Avoid heavy machinery on wet soil."
        },
        {
            "title": "Seed Quality Testing",
            "content": "Test seed germination rate before planting. Place 100 seeds on moist paper towel. Count germinated seeds after 7 days. Use seeds with 85%+ germination rate for best results."
        }
    ]
    
    # Generate embeddings for all documents
    documents = []
    embeddings = []
    
    for doc in knowledge_base:
        documents.append(doc)
        embedding = embedding_model.embed_text(doc['content'])
        embeddings.append(embedding)
    
    # Add to vector database
    vector_db.add_documents(documents, embeddings)
    print(f"[RAG] Knowledge base initialized with {len(documents)} documents")
    print()

# Initialize knowledge base on module load
initialize_knowledge_base()

def knowledge_base_search_worker(text, session_context):
    """RAG-based FAQ worker using local embedding model and vector DB"""
    print(f"[WORKFLOW] Knowledge Base Worker: Starting RAG-based FAQ search...")
    
    # Generate embedding for user query
    print(f"[WORKFLOW] Knowledge Base Worker: Generating query embedding...")
    query_embedding = embedding_model.embed_text(text)
    
    # Search vector database for relevant documents
    print(f"[WORKFLOW] Knowledge Base Worker: Searching vector database...")
    relevant_docs = vector_db.search(query_embedding, top_k=3)
    
    print(f"[WORKFLOW] Knowledge Base Worker: Found {len(relevant_docs)} relevant documents")
    
    # Build context from retrieved documents
    if relevant_docs:
        retrieved_context = "\n\n".join([
            f"Document {i+1} ({doc['title']}): {doc['content']}"
            for i, doc in enumerate(relevant_docs)
        ])
        
        # Create RAG-enhanced prompt
        prompt = f"""You are an agricultural FAQ expert. Use the following relevant documents to answer the user's question.

RELEVANT DOCUMENTS:
{retrieved_context}

USER QUESTION: {text}
SESSION CONTEXT: {session_context}

Instructions:
1. Answer the question using information from the provided documents
2. If the documents don't contain relevant information, say so
3. Be concise and accurate
4. Cite which document(s) you used for your answer

Answer:"""
    else:
        # Fallback if no relevant documents found
        prompt = f"""You are an agricultural FAQ expert. Answer the following question based on your knowledge.

USER QUESTION: {text}
SESSION CONTEXT: {session_context}

Note: No specific documents were found for this query, so answer based on general agricultural knowledge.

Answer:"""
    
    print(f"[WORKFLOW] Knowledge Base Worker: Calling LLM with RAG-enhanced prompt...")
    llm_output = ollama_client.generate_response(prompt)
    print(f"[WORKFLOW] Knowledge Base Worker: LLM response received")
    
    # Prepare result with source information
    sources = [doc['title'] for doc in relevant_docs] if relevant_docs else []
    result = {
        "answer": llm_output,
        "sources": sources,
        "num_sources": len(sources)
    }
    
    print(f"[WORKFLOW] Knowledge Base Worker: Result = {result}")
    return result

# --- Specialized Workers (now LLM-powered) ---
def plant_diagnosis_worker(image_bytes, session_context):
    print(f"[WORKFLOW] Plant Diagnosis Worker: Starting image analysis...")
    # LLM: Diagnose from Image
    prompt = f"You are a plant pathologist. Analyze the following image and provide a diagnosis and crop type. Context: {session_context}"
    # In a real system, you would encode the image or describe it; here, we use a placeholder string
    image_desc = vision.process_image(image_bytes) if image_bytes else "No image provided."
    llm_input = f"Image Description: {image_desc}\n{prompt}"
    print(f"[WORKFLOW] Plant Diagnosis Worker: Calling LLM for diagnosis...")
    llm_output = ollama_client.generate_response(llm_input)
    print(f"[WORKFLOW] Plant Diagnosis Worker: LLM response received")
    # Placeholder parse: extract diagnosis/crop_type from LLM output
    result = {"diagnosis": llm_output, "crop_type": "wheat"}  # TODO: parse real output
    print(f"[WORKFLOW] Plant Diagnosis Worker: Result = {result}")
    return result

# --- Structured Response Parsing for Crop Planner Worker ---
def crop_planner_worker(text, session_context):
    print(f"[WORKFLOW] Crop Planner Worker: Starting crop advice generation...")
    prompt = f"""You are a crop planner. Analyze the user's query and provide structured crop advice.

USER QUERY: {text}
SESSION CONTEXT: {session_context}

RESPOND IN THIS EXACT FORMAT:
CROP_TYPE: [extract or infer crop type from user input]
REGION: [extract or infer region from context or user input]
ADVICE: [detailed advice based on the query]

EXAMPLES:
- If user mentions 'cabbage' → CROP_TYPE: cabbage
- If user mentions 'wheat' → CROP_TYPE: wheat
- If context has region → use that, otherwise infer from query
- ADVICE should directly address the user's specific question

IMPORTANT: Extract crop type from user input, don't use hardcoded values."""
    print(f"[WORKFLOW] Crop Planner Worker: Calling LLM for crop advice...")
    llm_output = ollama_client.generate_response(prompt)
    print(f"[WORKFLOW] Crop Planner Worker: LLM response received")
    result = {}
    for line in llm_output.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip().lower()] = value.strip()
    if not result:
        crops = ["cabbage", "wheat", "tomato", "corn", "rice", "potato"]
        detected_crop = "unknown"
        for crop in crops:
            if crop.lower() in text.lower():
                detected_crop = crop
                break
        result = {
            "advice": llm_output,
            "crop_type": detected_crop,
            "region": session_context.get("region", "unknown")
        }
    print(f"[WORKFLOW] Crop Planner Worker: Result = {result}")
    return result

def fertilizer_planner_worker(text, session_context):
    print(f"[WORKFLOW] Fertilizer Planner Worker: Starting fertilizer plan generation...")
    # LLM: Fertilizer Plan Generation
    prompt = f"You are a fertilizer and irrigation planner. Given the following user query and context, provide a fertilizer plan and last fertilizer given.\nQuery: {text}\nContext: {session_context}"
    print(f"[WORKFLOW] Fertilizer Planner Worker: Calling LLM for fertilizer plan...")
    llm_output = ollama_client.generate_response(prompt)
    print(f"[WORKFLOW] Fertilizer Planner Worker: LLM response received")
    result = {"advice": llm_output, "last_fertilizer": "NPK"}  # TODO: parse real output
    print(f"[WORKFLOW] Fertilizer Planner Worker: Result = {result}")
    return result

# def knowledge_base_search_worker(text, session_context):
#     print(f"[WORKFLOW] Knowledge Base Worker: Starting FAQ search...")
#     # LLM: Answer FAQ
#     prompt = f"You are an agricultural FAQ expert. Given the following question and context, answer concisely.\nQuestion: {text}\nContext: {session_context}"
#     print(f"[WORKFLOW] Knowledge Base Worker: Calling LLM for FAQ answer...")
#     llm_output = ollama_client.generate_response(prompt)
#     print(f"[WORKFLOW] Knowledge Base Worker: LLM response received")
#     result = {"answer": llm_output}
#     print(f"[WORKFLOW] Knowledge Base Worker: Result = {result}")
#     return result

def sustainability_worker(text, session_context):
    print(f"[WORKFLOW] Sustainability Worker: Starting soil health analysis...")
    # LLM: Soil & Sustainability Advice
    prompt = f"You are a soil health and sustainability expert. Given the following user query and context, provide soil status and advice.\nQuery: {text}\nContext: {session_context}"
    print(f"[WORKFLOW] Sustainability Worker: Calling LLM for soil advice...")
    llm_output = ollama_client.generate_response(prompt)
    print(f"[WORKFLOW] Sustainability Worker: LLM response received")
    result = {"soil_status": "Low nitrogen", "advice": llm_output}  # TODO: parse real output
    print(f"[WORKFLOW] Sustainability Worker: Result = {result}")
    return result

# --- Intent Classifier (now LLM-powered) ---
def classify_intent_llm(text, session_context):
    print(f"[WORKFLOW] Intent Classifier: Classifying intent for text: '{text[:50]}...'")
    prompt = f"""You are an agricultural intent classifier. Analyze the user's input and classify their intent.

USER INPUT: {text}
CURRENT SESSION CONTEXT: {session_context}

INTENT CATEGORIES:
- crop_advice: Questions about planting, growing, crop selection, timing, crop problems, pests affecting crops
- fertilizer: Questions about fertilizers, nutrients, feeding plants, NPK, organic fertilizers
- soil_health: Questions about soil quality, soil problems, soil improvement, soil drying, soil becoming dead
- faq: General questions, how-to, what-is, why questions, general agricultural knowledge

CLASSIFICATION RULES:
- If the user mentions 'soil', 'drying', 'dead soil', 'soil quality' → soil_health
- If the user mentions 'fertilizer', 'nutrients', 'feeding' → fertilizer
- If the user mentions specific crops, planting, growing, pests → crop_advice
- Otherwise → faq

Respond with ONLY the intent label: crop_advice, fertilizer, soil_health, or faq."""
    print(f"[WORKFLOW] Intent Classifier: Calling LLM for intent classification...")
    llm_output = ollama_client.generate_response(prompt)
    print(f"[WORKFLOW] Intent Classifier: LLM response received")
    intent = llm_output.strip().lower().split()[0]
    valid_intents = ["crop_advice", "fertilizer", "faq", "soil_health"]
    final_intent = intent if intent in valid_intents else "faq"
    print(f"[WORKFLOW] Intent Classifier: Classified intent = {final_intent}")
    return final_intent

# --- Input Router with Language Detection ---
def input_router(image, audio, text):
    """
    Enhanced input router with language detection capabilities.
    Returns input type and detected language information.
    """
    detected_language = None
    
    if image:
        print(f"[WORKFLOW] Input Router: Detected IMAGE input")
        return "image", detected_language
    elif audio:
        print(f"[WORKFLOW] Input Router: Detected VOICE input")
        # Detect language from audio
        detected_language = language_detector.detect_audio_language(audio)
        print(f"[WORKFLOW] Language Detection: Audio language detected as {detected_language['language_name']} ({detected_language['language_code']})")
        return "voice", detected_language
    else:
        print(f"[WORKFLOW] Input Router: Detected TEXT input")
        # Detect language from text
        detected_language = language_detector.detect_text_language(text)
        print(f"[WORKFLOW] Language Detection: Text language detected as {detected_language['language_name']} ({detected_language['language_code']})")
        return "text", detected_language

# --- Context Validation and Update Logic ---
def validate_and_update_context(session_id, updates, user_input, session_context):
    validated_updates = {}
    crops = ["wheat", "cabbage", "tomato", "corn", "rice", "potato"]
    for crop in crops:
        if crop.lower() in user_input.lower():
            validated_updates["crop_type"] = crop
            break
    regions = ["punjab", "pakistan", "india", "usa", "canada"]
    for region in regions:
        if region.lower() in user_input.lower():
            validated_updates["region"] = region
            break
    validated_updates.update(updates)
    if validated_updates.get("crop_type") and validated_updates["crop_type"] != session_context.get("crop_type"):
        print(f"[WORKFLOW] Context Update: Crop type changed from {session_context.get('crop_type')} to {validated_updates['crop_type']}")
    if validated_updates:
        update_context(session_id, validated_updates)
        return validated_updates
    return {}

# --- Context-Aware Prompt Builder ---
def build_context_aware_prompt(worker_outputs, session_context, user_input, prev_context, language_info=None):
    user_crops = []
    crops = ["wheat", "cabbage", "tomato", "corn", "rice", "potato"]
    for crop in crops:
        if crop.lower() in user_input.lower():
            user_crops.append(crop)
    context_summary = []
    if session_context:
        context_summary.append(f"Session Context: {session_context}")
    if user_crops:
        context_summary.append(f"User mentioned crops: {', '.join(user_crops)}")
    if worker_outputs:
        context_summary.append(f"Worker Analysis: {worker_outputs}")
    prompt_parts = []
    
    # Add language instruction if language is detected and not English
    if language_info and language_info.get('language_code') != 'en':
        language_name = language_info.get('language_name', 'the detected language')
        prompt_parts.append(f"IMPORTANT: Please respond in {language_name}. The user is speaking in {language_name}.")
    
    if prev_context:
        prompt_parts.append(f"Previous Conversation:\n{prev_context}")
    if context_summary:
        prompt_parts.append(f"Current Context:\n{chr(10).join(context_summary)}")
    prompt_parts.append(f"User Query: {user_input}")
    return "\n\n".join(prompt_parts)

# --- Safe LLM Call ---
def safe_llm_call(prompt, fallback_response, context_info=""):
    try:
        print(f"[WORKFLOW] LLM Call: {context_info}")
        response = ollama_client.generate_response(prompt)
        if not response or response.strip() == "":
            print(f"[WORKFLOW] LLM returned empty response, using fallback")
            return fallback_response
        return response
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return fallback_response

class MultimodalServicer(multimodal_pb2_grpc.MultimodalServiceServicer):
    def Analyze(self, request, context):
        print()
        print(f"[WORKFLOW] ===== Starting new request =====")
        session_id = request.session_id or "default"
        # Improved input detection
        image = request.image if hasattr(request, 'image') and request.image and len(request.image) > 0 else None
        audio_path = request.audio_path if hasattr(request, 'audio_path') and request.audio_path and request.audio_path.strip() else None
        text = request.text.strip() if request.text else ""
        print(f"[WORKFLOW] Request details - Session: {session_id}, Has Image: {image is not None}, Has Audio: {audio_path is not None}, Text: '{text[:50]}...'")
        session_context = get_context(session_id)
        prev_messages = chat_memory.get_history(session_id)
        prev_context = "\n".join([f"{m['role']}: {m['message']}" for m in prev_messages])
        print(f"[WORKFLOW] Session context loaded: {session_context}")
        print(f"[WORKFLOW] Previous messages count: {len(prev_messages)}")
        input_type, detected_language = input_router(image, audio_path, text)
        worker_outputs = {}
        memory_updates = {}
        
        # Store detected language in session context
        if detected_language:
            session_context['detected_language'] = detected_language
            print(f"[WORKFLOW] Language Context: Stored {detected_language['language_name']} in session context")
        
        if input_type == "image":
            print(f"[WORKFLOW] Processing IMAGE input...")
            diagnosis = plant_diagnosis_worker(image, session_context)
            worker_outputs.update(diagnosis)
            memory_updates.update({k: v for k, v in diagnosis.items() if k in ["diagnosis", "crop_type"]})
            print(f"[WORKFLOW] Image processing complete. Memory updates: {memory_updates}")
        elif input_type == "voice":
            print(f"[WORKFLOW] Processing VOICE input with enhanced audio processing...")
            
            # Use enhanced audio processing that combines audio-based intent classification with text input
            audio_processing_result = asr.process_audio_with_enhanced_intent(audio_path, text, session_context)
            
            transcribed_text = audio_processing_result["transcribed_text"]
            audio_intent = audio_processing_result["audio_intent"]
            combined_text = audio_processing_result["combined_text"]
            final_intent = audio_processing_result["final_intent"]
            
            print(f"[WORKFLOW] Audio transcription: '{transcribed_text}'")
            print(f"[WORKFLOW] Audio-based intent: {audio_intent}")
            print(f"[WORKFLOW] Combined text: '{combined_text}'")
            print(f"[WORKFLOW] Final intent: {final_intent}")
            
            # Use the combined text and final intent for routing
            if final_intent == "crop_advice":
                print(f"[WORKFLOW] Routing to Crop Planner...")
                out = crop_planner_worker(combined_text, session_context)
                worker_outputs.update(out)
                memory_updates.update({k: v for k, v in out.items() if k in ["crop_type", "region"]})
            elif final_intent == "fertilizer":
                print(f"[WORKFLOW] Routing to Fertilizer Planner...")
                out = fertilizer_planner_worker(combined_text, session_context)
                worker_outputs.update(out)
                memory_updates.update({k: v for k, v in out.items() if k in ["last_fertilizer"]})
            elif final_intent == "faq":
                print(f"[WORKFLOW] Routing to Knowledge Base...")
                out = knowledge_base_search_worker(combined_text, session_context)
                worker_outputs.update(out)
            elif final_intent == "soil_health":
                print(f"[WORKFLOW] Routing to Sustainability Worker...")
                out = sustainability_worker(combined_text, session_context)
                worker_outputs.update(out)
                memory_updates.update({k: v for k, v in out.items() if k in ["soil_status"]})
        else:
            print(f"[WORKFLOW] Processing TEXT input...")
            intent = classify_intent_llm(text, session_context)
            print(f"[WORKFLOW] Text intent classified as: {intent}")
            if intent == "crop_advice":
                print(f"[WORKFLOW] Routing to Crop Planner...")
                out = crop_planner_worker(text, session_context)
                worker_outputs.update(out)
                memory_updates.update({k: v for k, v in out.items() if k in ["crop_type", "region"]})
            elif intent == "fertilizer":
                print(f"[WORKFLOW] Routing to Fertilizer Planner...")
                out = fertilizer_planner_worker(text, session_context)
                worker_outputs.update(out)
                memory_updates.update({k: v for k, v in out.items() if k in ["last_fertilizer"]})
            elif intent == "faq":
                print(f"[WORKFLOW] Routing to Knowledge Base...")
                out = knowledge_base_search_worker(text, session_context)
                worker_outputs.update(out)
            elif intent == "soil_health":
                print(f"[WORKFLOW] Routing to Sustainability Worker...")
                out = sustainability_worker(text, session_context)
                worker_outputs.update(out)
                memory_updates.update({k: v for k, v in out.items() if k in ["soil_status"]})
        # Improved context validation and update
        memory_updates = validate_and_update_context(session_id, memory_updates, text, session_context)
        if memory_updates:
            print(f"[WORKFLOW] Updating session context with: {memory_updates}")
            session_context.update(memory_updates)
        else:
            print(f"[WORKFLOW] No memory updates needed")
        # Build context-aware prompt with language information
        print(f"[WORKFLOW] Building final prompt for Response Generator LLM...")
        
        # Use combined text for voice inputs, otherwise use original text
        final_user_input = text
        if input_type == "voice" and 'combined_text' in locals():
            final_user_input = combined_text
            print(f"[WORKFLOW] Using combined text for voice input: '{final_user_input}'")
        
        # Get language information from session context
        language_info = session_context.get('detected_language')
        if language_info:
            print(f"[WORKFLOW] Language Context: Using {language_info['language_name']} for response generation")
        
        prompt = build_context_aware_prompt(worker_outputs, session_context, final_user_input, prev_context, language_info)
        print(f"[WORKFLOW] Final prompt length: {len(prompt)} characters")
        print(f"[WORKFLOW] Response Generator LLM: Calling LLM for final response...")
        text_output = ollama_client.generate_response(prompt)
        print(f"[WORKFLOW] Response Generator LLM: Final response received")
        print(f"[WORKFLOW] Updating chat history and logs...")
        
        # Use combined text for voice inputs in chat memory
        user_message = final_user_input if input_type == "voice" else (text or str(worker_outputs))
        chat_memory.add_message(session_id, "User", user_message)
        chat_memory.add_message(session_id, "Assistant", text_output)
        logger.log_entry("mixed", prompt, text_output)
        print(f"[WORKFLOW] ===== Request processing complete =====")
        
        # Get language information for response
        detected_language_code = ""
        detected_language_name = ""
        if detected_language:
            detected_language_code = detected_language.get('language_code', '')
            detected_language_name = detected_language.get('language_name', '')
        
        return multimodal_pb2.MultimodalResponse(
            text_output=text_output,
            detected_language_code=detected_language_code,
            detected_language_name=detected_language_name
        )


def serve():
    # Start automatic session cleanup
    session_manager.start_automatic_cleanup()
    print("Session manager started with automatic cleanup")
    
    # Configure server with larger message size limits
    server_options = [
        ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB send limit
        ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB receive limit
    ]
    
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=server_options
    )
    multimodal_pb2_grpc.add_MultimodalServiceServicer_to_server(MultimodalServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("MultimodalService gRPC server started on port 50051.")
    print("Message size limits: 50MB send/receive")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down server...")
        session_manager.stop_automatic_cleanup()
        server.stop(0)
