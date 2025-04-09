# rag_assistant.py
from langchain_community.llms import Ollama
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import os
import sys

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the personal_info.md file - fix the path using absolute path
personal_info_path = os.path.join(script_dir, 'data', 'generated', 'personal_info.md')
print(f"Loading personal info from: {personal_info_path}")
loader = TextLoader(personal_info_path)
documents = loader.load()

# Add metadata to documents for better context
for doc in documents:
    doc.metadata["source"] = "personal_information"
    doc.metadata["owner"] = "John Doe"
    doc.metadata["role"] = "Your owner's personal information"

# Split the text into smaller chunks for better embedding
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
split_documents = text_splitter.split_documents(documents)

# Create embeddings and vector store
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectordb = Chroma.from_documents(split_documents, embeddings)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})  # Get more documents for better context

# Create a custom prompt template that clearly defines the assistant's role
system_template = """You are OLIVER, a personal AI assistant to John Doe.
You have access to John's personal information in your knowledge base.
When answering questions, assume you are talking directly to John (your owner).
Any information retrieved is John's personal information.

IMPORTANT: You should NEVER mention "dossier", "file", "database", or "retrieved information" in your responses.
Simply treat all information as something you naturally know about John. Do not say phrases like "according to your information" or "I can see from your details".

Here is relevant information about John Doe:
{context}

Current conversation:
{chat_history}

John: {question}
OLIVER:"""

PROMPT = PromptTemplate(
    input_variables=["context", "chat_history", "question"],
    template=system_template,
)

# Initialize memory for better conversation handling
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="question",
    output_key="answer"
)

# Initialize the LLM
llm = Ollama(model='oliver-assistant')

# Create the Conversational Retrieval Chain with improved configuration
qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": PROMPT},
    return_source_documents=False,
    verbose=True  # Set to True to see the intermediate steps, helpful for debugging
)

# Test the retriever with a sample query
def test_retriever():
    sample_query = "What is my blood type?"
    results = retriever.get_relevant_documents(sample_query)
    print("Retriever Test Results:")
    for i, result in enumerate(results):
        print(f"\n--- Document {i+1} ---")
        print(f"Content: {result.page_content}")
        print(f"Metadata: {result.metadata}")

def print_help():
    """Print available commands"""
    print("\nAvailable Commands:")
    print("  /set            Set session variables")
    print("  /show           Show model information")
    print("  /load <model>   Load a session or model")
    print("  /save <model>   Save your current session")
    print("  /clear          Clear session context")
    print("  /bye            Exit")
    print("  /help, /?       Help for a command")
    print("  /test           Run retriever test")
    print("\nUse \"\"\" to begin a multi-line message.\n")
    print(">>> Send a message (/? for help)")

def handle_command(command, chat_history):
    """Handle slash commands"""
    cmd = command.strip().lower()
    
    if cmd in ['/?', '/help']:
        print_help()
    elif cmd == '/bye':
        print("Goodbye!")
        sys.exit(0)
    elif cmd == '/clear':
        chat_history.clear()
        print("Session context cleared.")
    elif cmd == '/test':
        test_retriever()
    elif cmd.startswith('/load '):
        model_name = cmd[6:].strip()
        print(f"Attempting to load model: {model_name}")
        try:
            global llm
            llm = Ollama(model=model_name)
            global qa
            qa = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=retriever,
                memory=memory,
                combine_docs_chain_kwargs={"prompt": PROMPT},
                return_source_documents=False,
                verbose=True
            )
            print(f"Model '{model_name}' loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
    elif cmd.startswith('/set'):
        print("Session variables feature not implemented yet.")
    elif cmd.startswith('/show'):
        print(f"Current model: {llm.model}")
    elif cmd.startswith('/save'):
        print("Session saving feature not implemented yet.")
    else:
        print(f"Unknown command: {command}")
        print_help()
    
    return chat_history

def interactive_chat():
    """Start an interactive chat session with command support"""
    chat_history = []
    
    # Print welcome message and help
    print("\n=== RAG Assistant Interactive Chat ===")
    print("Welcome! This assistant can answer questions based on your personal information.")
    print_help()
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input(">>> ")
            
            # Check if it's a command (starts with /)
            if user_input.startswith('/'):
                chat_history = handle_command(user_input, chat_history)
                continue
                
            # Check for multi-line input
            if user_input.strip() == '"""':
                print("Enter your multi-line message. Type \"\"\" on a new line to end.")
                multiline_input = []
                while True:
                    line = input()
                    if line.strip() == '"""':
                        break
                    multiline_input.append(line)
                user_input = '\n'.join(multiline_input)
                print(f"Received multi-line input ({len(multiline_input)} lines)")
            
            # Skip empty inputs
            if not user_input.strip():
                continue
                
            # Process the query
            response = qa({"question": user_input, "chat_history": chat_history})
            answer = response["answer"]
            
            # Update chat history
            chat_history.append((user_input, answer))
            
            # Print the response
            print(f"\n{answer}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # If arguments are provided, use the original behavior
    if len(sys.argv) > 1:
        # Test the retriever
        test_retriever()

        # Example query for the QA chain
        query = "Can you tell me a bit about my family?"
        chat_history = []
        response = qa({"question": query, "chat_history": chat_history})
        print(response["answer"])
    else:
        # Start interactive mode
        interactive_chat()
