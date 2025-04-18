#!/usr/bin/env python3
"""
Ollama Personal Assistant with RAG (Retrieval Augmented Generation)

This module serves as the main entry point for the Ollama Personal Assistant,
providing command-line interface to access various functionalities.
"""

import argparse
import os
import sys
from typing import Optional

from api.endpoints import start_api_server
from generation.generator import generate_personal_info
from rag.interactive import start_interactive_session
from config.template_config import OUTPUT_DOCUMENT
from config.rag_config import OLLAMA_DEFAULT_MODEL


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Ollama Personal Assistant with RAG capabilities",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # API server command
    api_parser = subparsers.add_parser("api", help="Start the RAG API server")
    api_parser.add_argument("--host", default="0.0.0.0", help="Host to bind the API server to")
    api_parser.add_argument("--port", type=int, default=8901, help="Port to bind the API server to")
    
    # Generate personal info command
    gen_parser = subparsers.add_parser("generate", help="Generate personal information markdown")
    gen_parser.add_argument("--output", help="Path to the output markdown file", default=OUTPUT_DOCUMENT)
    
    # Interactive RAG session command
    interactive_parser = subparsers.add_parser("interactive", help="Start an interactive RAG session")
    interactive_parser.add_argument("--model", default=OLLAMA_DEFAULT_MODEL, help="Ollama model to use")
    interactive_parser.add_argument("--markdown-file", default=OUTPUT_DOCUMENT, 
                                   help="Markdown file with personal information")
    
    # Ollama model creation command
    model_parser = subparsers.add_parser("create-model", help="Create a custom Ollama model")
    model_parser.add_argument("--name", required=True, help="Name of the model to create")
    model_parser.add_argument("--modelfile", required=True, help="Path to the Modelfile")
    
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the application.
    
    Parses command line arguments and routes to the appropriate functionality.
    """
    args = parse_args()
    
    if args.command == "api":
        # Start API server using uvicorn programmatically
        start_api_server(host=args.host, port=args.port)
    elif args.command == "generate":
        # Generate personal information markdown using the template_config approach
        generate_personal_info(output_path=args.output)
    elif args.command == "interactive":
        # Start interactive RAG session
        start_interactive_session(args.model, args.markdown_file)
    elif args.command == "create-model":
        # Create custom Ollama model
        import subprocess
        subprocess.run(["ollama", "create", args.name, "-f", args.modelfile], check=True)
    else:
        print("Please specify a command. Use --help for more information.")
        sys.exit(1)


if __name__ == "__main__":
    main()