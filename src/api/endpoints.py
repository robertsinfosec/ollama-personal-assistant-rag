"""
FastAPI implementation for the RAG assistant with Ollama-compatible API endpoints.
"""

import os
import json
import time
import asyncio
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag.assistant import RAGAssistant
from config.rag_config import OLLAMA_DEFAULT_MODEL, OLLAMA_API_HOST

# Define models.json path for storing available models
MODELS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "models.json")

# Define API models
class QueryRequest(BaseModel):
    """Model for query requests."""
    query: str
    model: Optional[str] = OLLAMA_DEFAULT_MODEL
    include_context: Optional[bool] = False
    k: Optional[int] = 3


class QueryResponse(BaseModel):
    """Model for query responses."""
    answer: str
    context: Optional[List[str]] = None


# Initialize FastAPI app
app = FastAPI(
    title="Ollama Personal Assistant API",
    description="API for interacting with a RAG-enhanced personal assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for assistant instances
assistant_instances = {}


def get_assistant(model: str = OLLAMA_DEFAULT_MODEL, markdown_file: str = "data/personal_info.md") -> RAGAssistant:
    """
    Get or create a RAG assistant instance.
    
    Args:
        model: The Ollama model to use
        markdown_file: Path to the markdown file
        
    Returns:
        RAGAssistant instance
        
    Raises:
        FileNotFoundError: If the markdown file doesn't exist
    """
    if not os.path.exists(markdown_file):
        raise FileNotFoundError(
            f"Markdown file not found: {markdown_file}\n"
            f"Please generate the markdown file first by running: python main.py generate"
        )
        
    key = f"{model}:{markdown_file}"
    if key not in assistant_instances:
        assistant_instances[key] = RAGAssistant(markdown_file=markdown_file, model=model)
    return assistant_instances[key]


@app.post("/query", response_model=QueryResponse)
async def query_assistant(request: QueryRequest) -> Dict[str, Any]:
    """
    Query the RAG assistant.
    
    Args:
        request: The query request with the question and options
        
    Returns:
        The assistant's response
    """
    try:
        assistant = get_assistant(request.model)
        answer, context = assistant.get_answer(request.query, k=request.k)
        
        response = {"answer": answer}
        if request.include_context:
            response["context"] = context
            
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reload")
async def reload_assistant(model: str = Query(OLLAMA_DEFAULT_MODEL, description="The model to reload")) -> Dict[str, str]:
    """
    Reload the vector store for a specific model.
    
    Args:
        model: The model to reload
        
    Returns:
        Success message
    """
    try:
        markdown_file = "data/personal_info.md"
        
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(
                f"Markdown file not found: {markdown_file}\n"
                f"Please generate the markdown file first by running: python main.py generate"
            )
        
        key = f"{model}:{markdown_file}"
        
        if key in assistant_instances:
            assistant_instances[key].reload_vector_store()
        else:
            # Create a new instance if it doesn't exist
            assistant_instances[key] = RAGAssistant(markdown_file=markdown_file, model=model)
            
        return {"status": "success", "message": f"Reloaded vector store for model {model}"}
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy"}


# --- Ollama-compatible API endpoints ---

@app.post("/api/chat")
async def chat(request: Request):
    """
    Ollama-compatible chat endpoint.
    
    Args:
        request: The raw request object containing the chat payload
        
    Returns:
        The response in Ollama-compatible format, either streaming or complete
    """
    try:
        # Extract the raw payload
        raw_body = await request.json()
        print("Received raw payload:", raw_body)  # For debugging
        
        # Extract and adapt the payload
        model = raw_body.get("model", OLLAMA_DEFAULT_MODEL)
        messages = raw_body.get("messages", [])
        stream = raw_body.get("stream", True)
        options = raw_body.get("options", {})
        
        if not messages or not isinstance(messages, list):
            return JSONResponse(
                {"error": "Invalid payload format. 'messages' must be a list."}, 
                status_code=422
            )

        # Extract the last user message as the question
        last_message = messages[-1]
        if last_message.get("role") != "user" or not last_message.get("content"):
            return JSONResponse(
                {"error": "Last message must be a user message with content."}, 
                status_code=422
            )
        question = last_message.get("content", "")
        
        # Get the assistant
        assistant = get_assistant(model)
        
        # Properly extract message pairs to build conversation history
        # We need to reconstruct question-answer pairs from the messages
        if len(messages) > 1:
            # Clear existing history to avoid contamination
            assistant.clear_history()
            
            # Go through messages and add them to history as pairs
            for i in range(0, len(messages)-1, 2):
                if i+1 < len(messages):
                    user_msg = messages[i]
                    assistant_msg = messages[i+1]
                    if (user_msg.get("role") == "user" and 
                        assistant_msg.get("role") == "assistant" and
                        "content" in user_msg and "content" in assistant_msg):
                        # Add to the assistant's history
                        assistant.conversation_history.append(
                            (user_msg["content"], assistant_msg["content"])
                        )
        
        # Process the request
        start_time = time.time()
        
        # Extract relevant parameters from options
        temperature = options.get("temperature", 0.7)
        top_p = options.get("top_p", 0.9)
        max_tokens = options.get("num_predict", 4096)
        k = options.get("top_k", 3)
        
        # Process the query with the same parameters as the interactive CLI
        answer, context = assistant.get_answer(
            query=question,
            k=k,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        
        print(f"Answer generated: {answer}")  # For debugging
        
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
    
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=404)
    except ConnectionError as e:
        return JSONResponse({"error": f"Connection error: {str(e)}"}, status_code=503)
    except Exception as e:
        print(f"Error in /api/chat: {e}")  # For debugging
        return JSONResponse({"error": f"Error processing request: {str(e)}"}, status_code=500)


def generate_models_json():
    """Generate models.json by querying the Ollama API at /api/tags."""
    try:
        print("Fetching model list from Ollama API...")
        # Use the configured Ollama API host instead of hardcoding localhost
        api_url = f"{OLLAMA_API_HOST}/api/tags"
        print(f"Using Ollama API URL: {api_url}")
        
        response = requests.get(api_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch models from Ollama API: {response.status_code}")

        models = response.json().get("models", [])
        if not models:
            raise Exception("No models returned from Ollama API")
            
        print(f"Fetched {len(models)} models from Ollama API.")

        # Save to models.json
        with open(MODELS_JSON_PATH, "w") as f:
            json.dump({"models": models}, f, indent=4)
        print(f"models.json successfully generated at {MODELS_JSON_PATH}")
        return True
    except Exception as e:
        print(f"Error generating models.json: {e}")
        # Don't create a minimal models.json with fake data
        # Instead, propagate the error
        return False


@app.get("/api/tags")
@app.get("/models")
async def list_models():
    """Endpoint to list available models."""
    try:
        # Regenerate the models.json file each time to ensure it's up-to-date
        success = generate_models_json()
        if not success:
            return JSONResponse({"error": "Failed to fetch models from Ollama API"}, status_code=500)
        
        if not os.path.exists(MODELS_JSON_PATH):
            return JSONResponse({"error": "Models file does not exist"}, status_code=500)
            
        with open(MODELS_JSON_PATH, "r") as f:
            data = json.load(f)
            
        if not data.get("models"):
            return JSONResponse({"error": "No models available"}, status_code=404)
            
        return data
    except Exception as e:
        return JSONResponse({"error": f"Failed to load models: {str(e)}"}, status_code=500)


@app.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """Endpoint to get information about a specific model."""
    try:
        # Regenerate the models.json file each time to ensure it's up-to-date
        success = generate_models_json()
        if not success:
            return JSONResponse({"error": "Failed to fetch models from Ollama API"}, status_code=500)
        
        if not os.path.exists(MODELS_JSON_PATH):
            return JSONResponse({"error": "Models file does not exist"}, status_code=500)
            
        with open(MODELS_JSON_PATH, "r") as f:
            data = json.load(f)
        
        if not data.get("models"):
            return JSONResponse({"error": "No models available"}, status_code=404)
            
        for model in data["models"]:
            if model.get("name", "").lower() == model_name.lower() or model.get("model", "").lower() == model_name.lower():
                return model
                
        return JSONResponse({"error": f"Model '{model_name}' not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": f"Failed to get model info: {str(e)}"}, status_code=500)


@app.get("/api/version")
async def get_version():
    """Endpoint to get the version of the API."""
    return {"version": "1.0.0"}


def start_api_server(host: str = "0.0.0.0", port: int = 8901) -> None:
    """
    Start the API server using uvicorn.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
    """
    # Generate models.json on startup
    # Instead of silently ignoring errors, provide a warning but continue starting the server
    models_loaded = generate_models_json()
    if not models_loaded:
        print("WARNING: Failed to load models from Ollama API on startup.")
        print("         Model endpoints may not function correctly until connection is restored.")
        print("         Check that the Ollama service is running and accessible.")
        print(f"         OLLAMA_API_HOST is set to: {OLLAMA_API_HOST}")
    
    print(f"Starting API server on {host}:{port}")
    print(f"Ollama Personal Assistant API with RAG capabilities is now available at http://{host}:{port}")
    print("Available endpoints:")
    print("  - /api/chat (POST): Ollama-compatible chat endpoint")
    print("  - /query (POST): Legacy RAG query endpoint")
    print("  - /models (GET): List available models")
    print("  - /models/{model_name} (GET): Get information about a specific model")
    print("  - /api/version (GET): Get API version")
    print("  - /reload (POST): Reload the vector store for a model")
    print("  - /health (GET): Health check endpoint")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # This allows the module to be run directly
    start_api_server()
