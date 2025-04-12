# Ollama Personal Assistant with RAG

This repository provides a complete solution for creating a personalized AI assistant powered by Ollama models and enhanced with Retrieval Augmented Generation (RAG).

## Table of Contents

- [Ollama Personal Assistant with RAG](#ollama-personal-assistant-with-rag)
  - [Table of Contents](#table-of-contents)
  - [Quick Start Guide](#quick-start-guide)
  - [Setting Up Your Environment](#setting-up-your-environment)
  - [Managing Your Personal Data](#managing-your-personal-data)
  - [Generating the Knowledge Base](#generating-the-knowledge-base)
  - [Creating Your Custom Ollama Model](#creating-your-custom-ollama-model)
  - [Running the RAG API Server](#running-the-rag-api-server)
  - [Using the Interactive CLI](#using-the-interactive-cli)
  - [Connecting to OpenWebUI](#connecting-to-openwebui)
  - [Command Reference](#command-reference)

## Quick Start Guide

If you've just cloned this repository, follow these steps to get your personal assistant up and running:

1. Set up a Python virtual environment
2. Install dependencies
3. Generate your personal information document
4. Create a custom Ollama model
5. Start the API server

## Setting Up Your Environment

Create a Python virtual environment and install the required dependencies:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Managing Your Personal Data

Your personal information is stored in YAML files in the `data/` directory:

- **Static data** (infrequently changing): `data/static/`
- **Dynamic data** (regularly updated): `data/dynamic/`

Customize these files with your personal information:

1. Edit the YAML files in `data/static/` (owner.yaml, family.yaml, etc.)
2. Update the dynamic data in `data/dynamic/` (calendar.yaml, tasks.yaml, etc.)
3. Modify the Jinja2 templates in `data/templates/` if needed

> [!TIP]
> See the [data module README](data/README.md) for detailed information about the data structure and format standards.

## Generating the Knowledge Base

After updating your personal data, generate the knowledge base document:

```bash
python main.py generate
```

This creates or updates `data/personal_info.md`, which serves as the central knowledge repository for your personal assistant.

> [!IMPORTANT]
> Re-run this command whenever you update your personal information to ensure your assistant has access to the latest data.

## Creating Your Custom Ollama Model

Create a custom Ollama model with the personality and behavior you want:

```bash
python main.py create-model --name oliver-assistant --modelfile models/Modelfile
```

This builds an Ollama model using the configuration in `models/Modelfile`. You can customize this file to adjust:

- The base model (e.g., llama3.2)
- Response style and personality
- Output formatting preferences
- Temperature and other parameters

> [!TIP]
> See the [models module README](models/README.md) for more information about model customization options.

## Running the RAG API Server

Start the API server to enable access to your RAG-enhanced personal assistant:

```bash
python main.py api
```

By default, the server runs on `0.0.0.0:8901`. You can specify a different host or port:

```bash
python main.py api --host 127.0.0.1 --port 8000
```

## Using the Interactive CLI

Test your personal assistant using the interactive command-line interface:

```bash
python main.py interactive
```

Add the `--verbose` flag to see the retrieved context for each response:

```bash
python main.py interactive --verbose
```

## Connecting to OpenWebUI

In OpenWebUI under `/admin/settings` go the Connections tab and click the `+` next to "Manage Ollama API Connections". Add a new connection with the following settings:

| Field                | Value                       |
| -------------------- | --------------------------- |
| URL                  | `http://[YOUR_API_HOST]:8901` |
| Prefix ID            | RAG (or whatever you want)  |
| "Add Model Id" field | `oliver-assistant`          |

Then click `Save`.

> [!IMPORTANT]
> The purpose of that `RAG` Prefix ID above is to differential models that come from your RAG endpoint, versus local models on the Ollama server. For example, this first `oliver-assistant` is the simple Ollama model on the Ollama server built with the `src/models/Modelfile` file:
>  
> ![alt text](../docs/images/rag1.png)
>
> The second `oliver-assistant` is the RAG model that you are hosting on your workstation, or API server (whatever `YOUR_API_HOST` IP address is, above:
>  
> ![alt text](../docs/images/rag2.png)

## Command Reference

The `main.py` script provides several commands:

```bash
python main.py --help
```

Available commands:

- `api`: Start the RAG API server
- `generate`: Generate personal information markdown
- `interactive`: Start an interactive RAG session
- `create-model`: Create a custom Ollama model

For detailed information about each command, use:

```bash
python main.py COMMAND --help
```

For example:

```bash
python main.py api --help
```

