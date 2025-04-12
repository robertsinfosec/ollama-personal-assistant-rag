"""
Configuration settings for the RAG assistant and Ollama integration.
"""

# Ollama API configuration
OLLAMA_API_HOST = "http://192.168.1.124:11434"  # Default Ollama API URL
OLLAMA_DEFAULT_MODEL = "oliver-assistant"       # Default model to use

# RAG configuration
DEFAULT_MARKDOWN_FILE = "data/personal_info.md"  # Default personal info file
DEFAULT_CHUNK_SIZE = 1000                        # Further increased chunk size to keep related information together
DEFAULT_CHUNK_OVERLAP = 200                      # Further increased chunk overlap to ensure context preservation
DEFAULT_TOP_K = 5                                # Default number of chunks to retrieve

# Generation parameters
DEFAULT_TEMPERATURE = 0.2                        # Lowered temperature for more factual responses
DEFAULT_TOP_P = 0.9                              # Default top-p for generation
DEFAULT_MAX_TOKENS = 1000                        # Default max tokens for generation

# Special separators for chunking to keep related information together
MARKDOWN_SEPARATORS = [
    # Headers are strong separators
    "\n## ",  # Major section (level 2 headers)
    "\n### ", # Subsection (level 3 headers)
    "\n#### ", # Sub-subsection (level 4 headers)
    # Tables and structured information
    "\n| ",   # Table rows
    "\n- ",   # List items
]

# Note: We've removed the RAG_SYSTEM_PROMPT and RAG_PROMPT_TEMPLATE
# as we want to use the built-in personality of the oliver-assistant model