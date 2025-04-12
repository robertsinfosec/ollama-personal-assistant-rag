# Ollama Personal Assistant API

This module provides a FastAPI implementation for the Retrieval Augmented Generation (RAG) assistant with Ollama-compatible API endpoints. The API enables integration of the personal assistant's capabilities into various applications and services.

## Table of Contents

- [Ollama Personal Assistant API](#ollama-personal-assistant-api)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [API Endpoints](#api-endpoints)
    - [Standard Endpoints](#standard-endpoints)
    - [Ollama-Compatible Endpoints](#ollama-compatible-endpoints)
  - [Request \& Response Models](#request--response-models)
    - [Query Request](#query-request)
    - [Query Response](#query-response)
  - [Starting the API Server](#starting-the-api-server)
  - [Error Handling](#error-handling)
  - [Example Usage](#example-usage)
    - [Basic Query Example (Python)](#basic-query-example-python)
    - [Using the Ollama-Compatible Chat API (curl)](#using-the-ollama-compatible-chat-api-curl)

## Overview

The Ollama Personal Assistant API serves as an interface to the RAG-enhanced personal assistant system. It provides endpoints for:

1. Querying the assistant with questions
2. Managing conversation context
3. Retrieving model information
4. Health monitoring
5. Compatibility with the Ollama API format

The API is designed to work with the pre-generated `personal_info.md` file, which contains the personal information used by the RAG system to provide context-aware responses.

> [!NOTE]
> Before using the API, ensure that you have generated the personal information markdown file by running `python main.py generate`.

## API Endpoints

### Standard Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/query` | Query the RAG assistant with a question |
| POST | `/reload` | Reload the vector store for a specific model |
| GET | `/health` | Health check endpoint |
| GET | `/models` | List available models |
| GET | `/models/{model_name}` | Get information about a specific model |

### Ollama-Compatible Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Ollama-compatible chat endpoint (supports streaming) |
| GET | `/api/tags` | Alternative endpoint for listing models (compatible with Ollama) |
| GET | `/api/version` | Get API version |

## Request & Response Models

### Query Request

```json
{
  "query": "What is my blood type?",
  "model": "llama2",
  "include_context": false,
  "k": 3
}
```

Parameters:
- `query` (required): The question to ask the assistant
- `model` (optional): The Ollama model to use (defaults to the value of `OLLAMA_DEFAULT_MODEL`)
- `include_context` (optional): Whether to include retrieved context in the response (defaults to `false`)
- `k` (optional): Number of context documents to retrieve (defaults to `3`)

### Query Response

```json
{
  "answer": "Your blood type is A+",
  "context": ["Health Information: Blood type: A+, Allergies: Peanuts, Penicillin"]
}
```

The `context` field is only included if `include_context` was set to `true` in the request.

> [!IMPORTANT]
> The `/api/chat` endpoint follows the Ollama API format for requests and responses, which is different from the format used by the `/query` endpoint. Please refer to the Ollama API documentation for details.

## Starting the API Server

The API server can be started in two ways:

1. Via the main entry point:
```
python src/main.py api [--host HOST] [--port PORT]
```

2. Directly from the module:
```
python -m src.api.endpoints
```

By default, the server listens on `0.0.0.0:8901`.

## Error Handling

The API provides descriptive error responses with appropriate HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 404 | Resource not found (e.g., markdown file, model) |
| 422 | Invalid request payload |
| 500 | Internal server error |
| 503 | Service unavailable (e.g., connection error to Ollama) |

Example error response:

```json
{
  "error": "Markdown file not found: data/personal_info.md\nPlease generate the markdown file first by running: python main.py generate"
}
```

## Example Usage

### Basic Query Example (Python)

```python
import requests

# Query the assistant
response = requests.post(
    "http://localhost:8901/query",
    json={
        "query": "What appointments do I have today?",
        "model": "llama2",
        "include_context": True
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Answer: {data['answer']}")
    
    if "context" in data:
        print("\nContext:")
        for i, ctx in enumerate(data["context"], 1):
            print(f"{i}. {ctx}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### Using the Ollama-Compatible Chat API (curl)

```bash
curl -X POST http://localhost:8901/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [
      {"role": "user", "content": "What appointments do I have today?"}
    ],
    "stream": false,
    "options": {
      "temperature": 0.7,
      "top_k": 3,
      "top_p": 0.9,
      "num_predict": 1024
    }
  }'
```

> [!TIP]
> To fetch streaming responses, set `"stream": true` in your request. This will return content incrementally as it's generated, improving perceived response time.