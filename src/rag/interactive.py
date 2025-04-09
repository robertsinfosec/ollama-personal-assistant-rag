"""
Interactive command-line interface for testing the RAG assistant.
"""

import os
from typing import Optional

from rag.assistant import RAGAssistant


def start_interactive_session(model: str = "mistral", markdown_file: str = "data/personal_info.md") -> None:
    """
    Start an interactive session with the RAG assistant.
    
    Args:
        model: Ollama model to use
        markdown_file: Path to the markdown file with personal information
        
    Raises:
        FileNotFoundError: If the markdown file doesn't exist
    """
    print(f"Initializing RAG assistant with model: {model}")
    
    # Check if markdown file exists before initializing RAGAssistant
    if not os.path.exists(markdown_file):
        raise FileNotFoundError(
            f"Markdown file not found: {markdown_file}\n"
            f"Please generate the markdown file first by running the generation script."
        )
    
    try:
        rag_assistant = RAGAssistant(markdown_file, model)
        print(f"Loaded personal information from {markdown_file}")
        print("Type 'quit', 'exit', or press Ctrl+C to end the session")
        print("Type 'reload' to reload the vector store")
        
        while True:
            try:
                query = input("\nQuestion: ").strip()
                
                if query.lower() in ["quit", "exit"]:
                    print("Exiting session. Goodbye!")
                    break
                
                if query.lower() == "reload":
                    rag_assistant.reload_vector_store()
                    print("Vector store reloaded!")
                    continue
                
                if not query:
                    continue
                
                answer, context = rag_assistant.get_answer(query)
                
                print("\nAnswer:", answer)
                print("\nRetrieved context:")
                for i, ctx in enumerate(context, 1):
                    print(f"\n--- Context {i} ---")
                    print(ctx)
                
            except KeyboardInterrupt:
                print("\nExiting session. Goodbye!")
                break
                
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # This allows the module to be run directly
    start_interactive_session()
