# Configuration Module

This module contains configuration settings for the Ollama Personal Assistant with RAG capabilities. The configuration is split into two main files:

1. `rag_config.py` - Configuration for the Retrieval Augmented Generation (RAG) system and Ollama integration
2. `template_config.py` - Configuration for the personal information template generation system

## Table of Contents

- [Configuration Module](#configuration-module)
  - [Table of Contents](#table-of-contents)
  - [Core Concept: The Personal Information Document](#core-concept-the-personal-information-document)
  - [RAG Configuration](#rag-configuration)
    - [Ollama API Settings](#ollama-api-settings)
    - [RAG Parameters](#rag-parameters)
    - [Generation Parameters](#generation-parameters)
    - [Chunking Configuration](#chunking-configuration)
  - [Template Configuration](#template-configuration)
    - [Section Mappings](#section-mappings)
    - [Header and Footer](#header-and-footer)
    - [Output Document](#output-document)
  - [Usage](#usage)
    - [Importing Configuration](#importing-configuration)
    - [Modifying Configuration](#modifying-configuration)

## Core Concept: The Personal Information Document

> [!IMPORTANT]
> The `personal_info.md` file is the cornerstone of this entire system. It serves as the central knowledge repository that powers the RAG-enhanced personal assistant.

This Markdown document is:
1. **Generated** by combining structured YAML data with Jinja2 templates (configured in `template_config.py`)
2. **Processed** by the RAG system which chunks it, creates embeddings, and stores them in a vector database
3. **Retrieved from** when users ask personal questions, allowing the assistant to provide contextually relevant, accurate responses

Everything in this repository essentially revolves around creating, maintaining, and leveraging this document for personalized AI assistance. The configuration files in this module control both how this document is generated and how it's processed by the RAG system.

When users interact with the assistant through the API or interactive CLI, the system:
1. Processes their question
2. Retrieves relevant chunks from the `personal_info.md` document
3. Uses these chunks as context for generating an accurate, personalized response

The quality, structure, and content of this document directly impact the assistant's ability to provide helpful, personalized responses.

## RAG Configuration

The `rag_config.py` file contains settings related to the Retrieval Augmented Generation system and the Ollama API integration.

### Ollama API Settings

```python
OLLAMA_API_HOST = "http://192.168.1.124:11434"  # Default Ollama API URL
OLLAMA_DEFAULT_MODEL = "oliver-assistant"       # Default model to use
```

These settings define the connection to the Ollama API server and the default model to use for generating responses.

> [!NOTE]
> The `OLLAMA_API_HOST` should be updated to match your Ollama server's location. The default value assumes the Ollama server is running on `192.168.1.124` at port `11434`.

### RAG Parameters

```python
DEFAULT_MARKDOWN_FILE = "data/personal_info.md"  # Default personal info file
DEFAULT_CHUNK_SIZE = 1000                        # Chunk size for text splitting
DEFAULT_CHUNK_OVERLAP = 200                      # Chunk overlap for context preservation
DEFAULT_TOP_K = 5                                # Default number of chunks to retrieve
```

These parameters control how the personal information document is processed for retrieval:

- `DEFAULT_MARKDOWN_FILE`: Path to the personal information markdown file
- `DEFAULT_CHUNK_SIZE`: Size of text chunks for vector storage (larger values keep related information together)
- `DEFAULT_CHUNK_OVERLAP`: Overlap between chunks to ensure context preservation
- `DEFAULT_TOP_K`: Number of most relevant chunks to retrieve for each query

### Generation Parameters

```python
DEFAULT_TEMPERATURE = 0.2                        # Temperature for generation
DEFAULT_TOP_P = 0.9                              # Top-p for generation
DEFAULT_MAX_TOKENS = 1000                        # Max tokens for generation
```

These parameters control the text generation process:

- `DEFAULT_TEMPERATURE`: Controls randomness in generation (lower values produce more deterministic outputs)
- `DEFAULT_TOP_P`: Controls nucleus sampling (concentration of probability mass)
- `DEFAULT_MAX_TOKENS`: Maximum number of tokens to generate in a response

### Chunking Configuration

```python
MARKDOWN_SEPARATORS = [
    "\n## ",   # Major section (level 2 headers)
    "\n### ",  # Subsection (level 3 headers)
    "\n#### ", # Sub-subsection (level 4 headers)
    "\n| ",    # Table rows
    "\n- ",    # List items
]
```

These separators guide the text chunking process, ensuring that related information stays together. The system will try to split text at these separator points to maintain coherent chunks.

## Template Configuration

The `template_config.py` file contains settings for the personal information template generation system, which combines YAML data files with Jinja2 templates to produce the final `personal_info.md` file.

### Section Mappings

```python
SECTION_MAPPINGS = [
    # Static data sections
    ("data/static/owner.yaml", "data/templates/owner.md.j2"),
    ("data/static/family.yaml", "data/templates/family.md.j2"),
    # ...more mappings...
    
    # Dynamic data sections
    ("data/dynamic/calendar.yaml", "data/templates/calendar.md.j2"),
    ("data/dynamic/messages.yaml", "data/templates/messages.md.j2"),
    # ...more mappings...
]
```

Each tuple in `SECTION_MAPPINGS` defines a pair of:
1. A YAML data file path
2. A corresponding Jinja2 template file path

The system processes each pair, loading data from the YAML file and rendering it with the template to generate a section of the final markdown document.

> [!IMPORTANT]
> The order of the mappings in this list determines the order of sections in the final markdown document.

### Header and Footer

```python
HEADER_TEMPLATE = "data/templates/header.md.j2"
FOOTER_TEMPLATE = "data/templates/footer.md.j2"
```

Optional templates for the document header and footer:
- `HEADER_TEMPLATE`: Rendered at the start of the document
- `FOOTER_TEMPLATE`: Rendered at the end of the document

### Output Document

```python
OUTPUT_DOCUMENT = "data/personal_info.md"
```

The path where the final generated markdown document will be saved.

## Usage

### Importing Configuration

Import the configuration values in your Python code:

```python
# For RAG configuration
from config.rag_config import (
    OLLAMA_API_HOST,
    OLLAMA_DEFAULT_MODEL,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_TOP_K
)

# For template configuration
from config.template_config import SECTION_MAPPINGS, OUTPUT_DOCUMENT
```

### Modifying Configuration

To modify the configuration:

1. Edit the appropriate configuration file directly
2. For temporary changes, override the imported values in your code:

```python
from config.rag_config import DEFAULT_TOP_K, DEFAULT_TEMPERATURE

# Override for a specific use case
custom_top_k = DEFAULT_TOP_K + 2  # Retrieve more context chunks
custom_temperature = 0.5  # Increase creativity in responses
```

> [!TIP]
> When modifying chunking parameters (`DEFAULT_CHUNK_SIZE` and `DEFAULT_CHUNK_OVERLAP`), you may need to regenerate your vector store for the changes to take effect. Use the `/reload` endpoint in the API or restart the interactive session.