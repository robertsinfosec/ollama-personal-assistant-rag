# api.py (FastAPI)
import subprocess
import json
import os
import requests  # Add this import
from fastapi import FastAPI, Request  # Import Request for raw payload access
from fastapi.responses import StreamingResponse, JSONResponse  # Import StreamingResponse and JSONResponse for responses
import asyncio  # Import asyncio for async operations
from pydantic import BaseModel
from rag_assistant import qa
from datetime import datetime  # Import datetime for timestamp
import time  # Import time for timestamp

MODELS_JSON_PATH = "./models.json"

# Initialize FastAPI
app = FastAPI()

class Query(BaseModel):
    question: str
    chat_history: list = []

@app.post("/api/chat")
async def chat(request: Request):
    # Log the raw incoming payload
    raw_body = await request.json()
    print("Received raw payload:", raw_body)

    # Extract and adapt the payload
    model = raw_body.get("model", "oliver-assistant")
    messages = raw_body.get("messages", [])
    stream = raw_body.get("stream", True)  # Default to streaming for this endpoint

    if not messages or not isinstance(messages, list):
        return JSONResponse({"error": "Invalid payload format. 'messages' must be a list."}, status_code=422)

    # Extract the last user message as the question
    question = messages[-1].get("content", "")
    chat_history = [
        {"role": msg.get("role"), "content": msg.get("content")}
        for msg in messages[:-1]  # Exclude the last message (current question)
    ]

    if not question:
        return JSONResponse({"error": "Invalid payload format. 'content' in the last message must be a string."}, status_code=422)

    # Process the query to get the answer
    start_time = time.time()
    result = qa({"question": question, "chat_history": chat_history})
    answer = result["answer"]
    print(f"Answer generated: {answer}")
    
    # For non-streaming requests, return the full answer
    if not stream:
        response_data = {
            "model": model,
            "created_at": datetime.now().isoformat() + "Z",
            "message": {
                "role": "assistant",
                "content": answer
            },
            "done": True,
            "done_reason": "stop",
            "total_duration": int((time.time() - start_time) * 1e9)  # Convert to nanoseconds
        }
        return JSONResponse(response_data)
        
    # For streaming requests, return the answer as a stream in Ollama-compatible format
    async def generate():
        process_start = time.time()
        
        # Stream the content in small chunks
        chunk_size = 4  # Small chunks for more responsive streaming
        for i in range(0, len(answer), chunk_size):
            chunk = answer[i:i + chunk_size]
            current_time = datetime.now().isoformat() + "Z"
            
            chunk_data = {
                "model": model,
                "created_at": current_time,
                "message": {
                    "role": "assistant",
                    "content": chunk
                },
                "done": False
            }
            yield json.dumps(chunk_data) + "\n"
            await asyncio.sleep(0.01)  # Small delay for more realistic streaming
        
        # Send the final chunk with done: true
        process_end = time.time()
        total_duration = int((process_end - process_start) * 1e9)  # Convert to nanoseconds
        
        final_chunk = {
            "model": model,
            "created_at": datetime.now().isoformat() + "Z",
            "message": {
                "role": "assistant",
                "content": ""
            },
            "done_reason": "stop",
            "done": True,
            "total_duration": total_duration,
            "load_duration": int(total_duration * 0.8),  # Simulated load duration
            "prompt_eval_count": len(question),
            "prompt_eval_duration": int(total_duration * 0.1),
            "eval_count": len(answer),
            "eval_duration": int(total_duration * 0.1)
        }
        yield json.dumps(final_chunk) + "\n"
        
    headers = {
        "Content-Type": "application/x-ndjson",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    
    return StreamingResponse(generate(), headers=headers, media_type="application/x-ndjson")

def generate_models_json():
    """Generate models.json by querying the Ollama API at /api/tags."""
    try:
        print("Fetching model list from Ollama API...")
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            raise Exception(f"Failed to fetch models from Ollama API: {response.status_code}")

        models = response.json().get("models", [])
        print(f"Fetched {len(models)} models from Ollama API.")

        # Save to models.json
        with open(MODELS_JSON_PATH, "w") as f:
            json.dump({"models": models}, f, indent=4)
        print("models.json successfully generated.")
    except Exception as e:
        print(f"Error generating models.json: {e}")

@app.get("/api/tags")
@app.get("/models")
async def list_models():
    """Endpoint to list available models."""
    try:
        with open(MODELS_JSON_PATH, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {"error": f"Failed to load models.json: {e}"}, 500

@app.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """Endpoint to get information about a specific model."""
    try:
        with open(MODELS_JSON_PATH, "r") as f:
            data = json.load(f)
        for model in data["models"]:
            if model["id"] == model_name.lower():
                return model
        return {"error": f"Model '{model_name}' not found"}, 404
    except Exception as e:
        return {"error": f"Failed to load models.json: {e}"}, 500

@app.get("/api/version")
async def get_version():
    """Endpoint to get the version of the API."""
    return {"version": "1.0.0"}


"""Generate models.json when the API starts."""
generate_models_json()