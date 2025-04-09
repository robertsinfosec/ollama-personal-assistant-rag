"""
FastAPI implementation for the RAG assistant.
"""

import os
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.assistant import RAGAssistant


# Define API models
class QueryRequest(BaseModel):
    """Model for query requests."""
    query: str
    model: Optional[str] = "mistral"
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


def get_assistant(model: str = "mistral", markdown_file: str = "data/personal_info.md") -> RAGAssistant:
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
            f"Please generate the markdown file first by running the generation script."
        )
        
    key = f"{model}:{markdown_file}"
    if key not in assistant_instances:
        assistant_instances[key] = RAGAssistant(markdown_file, model)
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
async def reload_assistant(model: str = Query("mistral", description="The model to reload")) -> Dict[str, str]:
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
                f"Please generate the markdown file first by running the generation script."
            )
        
        key = f"{model}:{markdown_file}"
        
        if key in assistant_instances:
            assistant_instances[key].reload_vector_store()
        else:
            # Create a new instance if it doesn't exist
            assistant_instances[key] = RAGAssistant(markdown_file, model)
            
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


def start_api_server(host: str = "0.0.0.0", port: int = 8901) -> None:
    """
    Start the API server using uvicorn.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
    """
    print(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # This allows the module to be run directly
    start_api_server()
