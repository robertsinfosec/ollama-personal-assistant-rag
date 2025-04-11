"""
Interactive command-line interface for testing the RAG assistant.
"""

import os
import sys
import logging
import argparse
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich import box

from rag.assistant import RAGAssistant
from config.rag_config import (
    OLLAMA_API_HOST, OLLAMA_DEFAULT_MODEL, DEFAULT_MARKDOWN_FILE,
    DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MAX_TOKENS, DEFAULT_TOP_K
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize rich console
console = Console()

def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the interactive session."""
    parser = argparse.ArgumentParser(description="Interactive RAG Assistant CLI")
    
    parser.add_argument("--model", type=str, default=OLLAMA_DEFAULT_MODEL,
                        help=f"Ollama model to use")
    parser.add_argument("--markdown-file", type=str, default=DEFAULT_MARKDOWN_FILE,
                        help=f"Markdown file with personal information")
    parser.add_argument("--verbose", action="store_true", help="Show retrieved context in responses")
    
    return parser.parse_args()

def display_help():
    """Display help information about available commands in a visually appealing format."""
    help_table = Table(show_header=True, box=box.ROUNDED, header_style="bold magenta")
    help_table.add_column("Command", style="cyan")
    help_table.add_column("Description")
    
    help_table.add_row("/help", "Show this help message")
    help_table.add_row("/quit, /exit", "Exit the interactive session")
    help_table.add_row("/reload", "Reload the vector store")
    help_table.add_row("/model MODEL", "Change the model (e.g., /model llama2)")
    help_table.add_row("/params", "Show current parameter settings")
    help_table.add_row("/temp VALUE", "Set temperature (0.0-1.0)")
    help_table.add_row("/topk VALUE", "Set number of context chunks to retrieve")
    help_table.add_row("/clear", "Clear the screen")
    help_table.add_row("/clear_history", "Clear conversation history")
    help_table.add_row("/context", "Toggle display of retrieved context")
    
    console.print(Panel(help_table, title="Available Commands", border_style="bright_blue"))

def handle_command(command: str, rag_assistant: RAGAssistant, params: dict) -> bool:
    """
    Handle special commands that start with '/'.
    
    Returns True if the session should continue, False if it should exit.
    """
    cmd_parts = command.strip().split()
    cmd = cmd_parts[0].lower()
    
    if cmd in ["/quit", "/exit"]:
        console.print("[bold yellow]Exiting session. Goodbye![/]")
        return False
        
    elif cmd == "/help":
        display_help()
        
    elif cmd == "/reload":
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Reloading vector store...[/]"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Reloading", total=None)
            rag_assistant.reload_vector_store()
            progress.update(task, completed=True)
        console.print("[bold green]✓[/] Vector store successfully reloaded!")
        
    elif cmd == "/model" and len(cmd_parts) > 1:
        new_model = cmd_parts[1]
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold blue]Changing model to {new_model}...[/]"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Changing", total=None)
                rag_assistant.set_model(new_model)
                progress.update(task, completed=True)
            console.print(f"[bold green]✓[/] Model changed to [bold]{new_model}[/]")
        except Exception as e:
            console.print(f"[bold red]✗ Error changing model:[/] {e}")
            
    elif cmd == "/params":
        params_table = Table(show_header=True, box=box.SIMPLE)
        params_table.add_column("Parameter", style="cyan")
        params_table.add_column("Value", style="green")
        
        params_table.add_row("Model", rag_assistant.model)
        params_table.add_row("Temperature", str(params['temperature']))
        params_table.add_row("Top-p", str(params['top_p']))
        params_table.add_row("Max Tokens", str(params['max_tokens']))
        params_table.add_row("Top-k", str(params['top_k']))
        params_table.add_row("Show Context", "ON" if params['show_context'] else "OFF")
        
        console.print(Panel(params_table, title="Current Parameters", border_style="bright_blue"))
        
    elif cmd == "/temp" and len(cmd_parts) > 1:
        try:
            value = float(cmd_parts[1])
            if 0.0 <= value <= 1.0:
                params['temperature'] = value
                console.print(f"[green]Temperature set to {value}[/]")
            else:
                console.print("[yellow]Temperature must be between 0.0 and 1.0[/]")
        except ValueError:
            console.print("[bold red]Invalid temperature value. Please use a number between 0.0 and 1.0[/]")
            
    elif cmd == "/topk" and len(cmd_parts) > 1:
        try:
            value = int(cmd_parts[1])
            if value > 0:
                params['top_k'] = value
                console.print(f"[green]Top-k set to {value}[/]")
            else:
                console.print("[yellow]Top-k must be a positive integer[/]")
        except ValueError:
            console.print("[bold red]Invalid top-k value. Please use a positive integer[/]")
            
    elif cmd == "/clear":
        console.clear()
        
    elif cmd == "/clear_history":
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Clearing conversation history...[/]"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Clearing", total=None)
            rag_assistant.clear_history()
            progress.update(task, completed=True)
        console.print("[bold green]✓[/] Conversation history cleared.")
        
    elif cmd == "/context":
        params['show_context'] = not params['show_context']
        status = "[green]ON[/]" if params['show_context'] else "[yellow]OFF[/]"
        console.print(f"Context display: {status}")
        
    else:
        console.print(f"[yellow]Unknown command:[/] {command}")
        console.print("Type [bold cyan]/help[/] for available commands")
        
    return True  # Continue the session

def start_interactive_session(
    model: str = OLLAMA_DEFAULT_MODEL, 
    markdown_file: str = DEFAULT_MARKDOWN_FILE,
    verbose: bool = False
) -> None:
    """
    Start an interactive session with the RAG assistant.
    
    Args:
        model: Ollama model to use
        markdown_file: Path to the markdown file with personal information
        verbose: Whether to display retrieved context
        
    Raises:
        FileNotFoundError: If the markdown file doesn't exist
        ConnectionError: If unable to connect to the Ollama server
    """
    # Store parameters that can be modified during the session
    params = {
        'temperature': DEFAULT_TEMPERATURE,
        'top_p': DEFAULT_TOP_P,
        'max_tokens': DEFAULT_MAX_TOKENS,
        'top_k': DEFAULT_TOP_K,
        'show_context': verbose
    }
    
    console.print(f"[bold blue]Initializing RAG assistant[/] with model: [green]{model}[/]")
    console.print(f"Using Ollama server at: [cyan]{OLLAMA_API_HOST}[/]")
    
    # Check if markdown file exists before initializing RAGAssistant
    if not os.path.exists(markdown_file):
        console.print(
            f"[bold red]✗ Markdown file not found:[/] {markdown_file}\n"
            f"Please generate the markdown file first by running: [bold]python ./main.py generate[/]",
            style="red"
        )
        sys.exit(1)
    
    try:
        # Show a spinner while initializing
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Initializing RAG Assistant...[/]"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Loading", total=None)
            rag_assistant = RAGAssistant(
                markdown_file=markdown_file,
                model=model,
                ollama_host=OLLAMA_API_HOST
            )
            progress.update(task, completed=True)
        
        console.print(f"[bold green]✓[/] Loaded personal information from [cyan]{markdown_file}[/]")
        
        # Display welcome message
        welcome_panel = Panel(
            "[bold]Type your questions or use / commands\n"
            "Type [cyan]/help[/] for available commands[/]",
            title="🤖 Interactive RAG Assistant", 
            border_style="bright_blue"
        )
        console.print(welcome_panel)
        
        while True:
            try:
                # Add visual separator between interactions
                console.print("─" * console.width, style="bright_black")
                
                # Get user question with styled prompt
                user_input = Prompt.ask("[bold green]Question[/]")
                
                # Skip empty inputs
                if not user_input:
                    continue
                    
                # Handle special commands
                if user_input.startswith('/'):
                    if not handle_command(user_input, rag_assistant, params):
                        break
                    continue
                
                # Process the query using current parameters with a spinner to show progress
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]Thinking...[/]"),
                    console=console,
                    transient=True
                ) as progress:
                    task = progress.add_task("Generating answer", total=None)
                    answer, context = rag_assistant.get_answer(
                        query=user_input,
                        k=params['top_k'],
                        temperature=params['temperature'],
                        top_p=params['top_p'],
                        max_tokens=params['max_tokens'],
                        system_prompt=None  # Respect model's system prompt
                    )
                    progress.update(task, completed=True)
                
                # Display the answer in a nicely formatted panel
                console.print(Panel(
                    Markdown(answer),
                    title="🤖 Answer",
                    border_style="green",
                    padding=(1, 2)
                ))
                
                # Display context information if enabled
                if params['show_context']:
                    context_table = Table(show_header=True, box=box.SIMPLE, header_style="bright_blue")
                    context_table.add_column("Context #", style="cyan")
                    context_table.add_column("Content")
                    
                    for i, ctx in enumerate(context, 1):
                        context_table.add_row(str(i), ctx[:500] + ("..." if len(ctx) > 500 else ""))
                    
                    console.print(Panel(
                        context_table,
                        title="Retrieved Context",
                        border_style="yellow"
                    ))
                
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Exiting session. Goodbye![/]")
                break
            except Exception as e:
                console.print(f"\n[bold red]Error:[/] {e}")
                
    except ConnectionError as e:
        console.print(f"[bold red]✗ Error connecting to Ollama server:[/] {e}")
        console.print(f"Please make sure Ollama is running at [cyan]{OLLAMA_API_HOST}[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]✗ Error initializing RAG assistant:[/] {e}")
        sys.exit(1)

if __name__ == "__main__":
    # This allows the module to be run directly
    args = parse_args()
    start_interactive_session(
        model=args.model,
        markdown_file=args.markdown_file,
        verbose=args.verbose
    )
