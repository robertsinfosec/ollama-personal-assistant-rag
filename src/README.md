# Setup Instructions:

## 1. Build your Ollama model:

```bash
ollama create oliver-assistant -f ./models/Modelfile
```

## 2. Install dependencies:

```bash
pip install -r ./requirements.txt
```

## 3. Update your personal information regularly

Modify the [`static/personal_info_static.yaml`](static/personal_info_static.yaml) file early and often.

## 4. Run your API server:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

## 5. Connect OpenWebUI to your API endpoint at:

http://localhost:8000/chat

Ensure that OpenWebUI sends requests formatted correctly as:

```json
{
  "question": "{{prompt}}",
  "chat_history": []
}
```

and expects responses formatted as:

```json
{
  "answer": "LLM Response"
}
```