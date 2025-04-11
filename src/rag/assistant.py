"""
Core RAG assistant functionality that retrieves relevant information and
augments LLM responses.
"""

import os
import re
import logging
import requests
from typing import Dict, List, Optional, Tuple, Union

# Updated imports for LangChain components
from langchain_text_splitters import MarkdownTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.embeddings import OllamaEmbeddings

# Import configuration
from config.rag_config import (
    OLLAMA_API_HOST, OLLAMA_DEFAULT_MODEL, DEFAULT_MARKDOWN_FILE,
    DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, DEFAULT_TOP_K,
    DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MAX_TOKENS,
    MARKDOWN_SEPARATORS
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGAssistant:
    """
    Retrieval Augmented Generation Assistant that enhances LLM responses
    with retrieved information from personal markdown documents.
    """
    
    def __init__(
        self, 
        markdown_file: str = DEFAULT_MARKDOWN_FILE, 
        model: str = OLLAMA_DEFAULT_MODEL,
        ollama_host: str = OLLAMA_API_HOST,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ):
        """
        Initialize the RAG Assistant.
        
        Args:
            markdown_file: Path to the markdown file with personal information
            model: Ollama model to use for embeddings and generation
            ollama_host: URL of the Ollama API server
            chunk_size: Size of text chunks for the vector store
            chunk_overlap: Overlap between text chunks
        """
        self.model = model
        self.markdown_file = markdown_file
        self.ollama_host = ollama_host
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_store = None
        self.conversation_history = []  # Store conversation history as (query, response) tuples
        
        # Format the base URL correctly
        self.base_url = self.ollama_host.rstrip('/')
        
        try:
            # Check if Ollama server is reachable using direct API call
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                raise ConnectionError(f"Failed to connect to Ollama server at {ollama_host}: Status code {response.status_code}")
            
            logger.info(f"Successfully connected to Ollama server at {ollama_host}")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama server at {ollama_host}: {e}")
            raise ConnectionError(f"Failed to connect to Ollama server at {ollama_host}: {e}")
            
        try:
            self._initialize_vector_store()
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def _preprocess_markdown(self, content: str) -> str:
        """
        Preprocess markdown content to improve chunking and retrieval.
        
        Args:
            content: The markdown content to preprocess
            
        Returns:
            Preprocessed markdown content
        """
        # Enhance content with better metadata handling
        
        # Process semantic search keywords
        # These comments will be kept visible for embedding but marked for special handling
        semantic_keywords = re.findall(r'<!-- SEMANTIC_SEARCH_KEYWORDS: (.*?) -->', content)
        for keywords in semantic_keywords:
            # Add the keywords as text that will be visible to the embedding model
            # but marked in a way that they won't appear in the output
            formatted_keywords = f"\n[SEARCH_TERMS: {keywords}]\n"
            content = content.replace(f"<!-- SEMANTIC_SEARCH_KEYWORDS: {keywords} -->", 
                                      f"<!-- SEMANTIC_SEARCH_KEYWORDS: {keywords} -->\n{formatted_keywords}")
        
        # Process summary comments - these contain natural language descriptions
        # that are helpful for retrieval but shouldn't be visible in output
        for comment_type in ['ADDRESS_SUMMARY', 'LOCATION_CONTEXT', 'RELATIONSHIP_STATUS', 
                            'CHILDREN_SUMMARY', 'PARENTS_SUMMARY', 'SIBLINGS_SUMMARY']:
            summaries = re.findall(f'<!-- {comment_type} (.*?) -->', content)
            for summary in summaries:
                # Add the summary as text that will be visible to the embedding model
                formatted_summary = f"\n[{comment_type}: {summary}]\n"
                content = content.replace(f"<!-- {comment_type} {summary} -->", 
                                         f"<!-- {comment_type} {summary} -->\n{formatted_summary}")
        
        # Keep original family relationship markers for backward compatibility
        content = re.sub(r'(#+\s*Family\s*Relationships?.*?)(\n\s*\|)', 
                         r'\1\n<!-- FAMILY_RELATIONSHIPS_START -->\2', 
                         content, flags=re.IGNORECASE)
        content = re.sub(r'(\n\s*\|.*Family\s*Relationships?.*?\n)(\s*#+)', 
                         r'\1<!-- FAMILY_RELATIONSHIPS_END -->\n\2', 
                         content, flags=re.IGNORECASE)
        
        # Keep original sibling information markers for backward compatibility
        content = re.sub(r'(\|.*?\|\s*Sibling.*?\|.*?\|)', 
                         r'<!-- SIBLING_INFO_START -->\1<!-- SIBLING_INFO_END -->', 
                         content, flags=re.IGNORECASE)
        
        return content
    
    def _initialize_vector_store(self) -> None:
        """
        Initialize the vector store with chunks from the markdown file.
        """
        if not os.path.exists(self.markdown_file):
            err_msg = f"Markdown file not found: {self.markdown_file}"
            logger.error(err_msg)
            raise FileNotFoundError(err_msg)
            
        logger.info(f"Loading markdown file: {self.markdown_file}")
        try:
            with open(self.markdown_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Preprocess markdown content for better chunking
            markdown_content = self._preprocess_markdown(markdown_content)
                
            # Use RecursiveCharacterTextSplitter with custom separators for better chunking
            logger.info(f"Splitting markdown into chunks (size={self.chunk_size}, overlap={self.chunk_overlap})")
            markdown_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size, 
                chunk_overlap=self.chunk_overlap,
                separators=MARKDOWN_SEPARATORS + ["\n\n", "\n", " ", ""]
            )
            chunks = markdown_splitter.split_text(markdown_content)
            logger.info(f"Created {len(chunks)} chunks from the markdown file")
            
            # Create vector store
            logger.info(f"Creating vector store using {self.model} embeddings")
            # Configure OllamaEmbeddings with the correct base_url parameter
            embeddings = OllamaEmbeddings(
                model=self.model,
                base_url=self.base_url
            )
            self.vector_store = FAISS.from_texts(chunks, embeddings)
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def _expand_query(self, query: str) -> List[str]:
        """
        Expand the query with relevant variations to improve retrieval.
        
        Args:
            query: The original query
            
        Returns:
            List of expanded queries
        """
        # Always start with the original query
        expanded_queries = [query]
        
        # Check if query is about family relationships (keep this as it's generally useful)
        family_keywords = ['family', 'sibling', 'sister', 'brother', 'parent', 'father', 'mother', 'spouse', 'wife', 'husband']
        
        if any(keyword in query.lower() for keyword in family_keywords):
            # Add relationship-specific variations
            if 'sibling' in query.lower() or 'brother' in query.lower() or 'sister' in query.lower():
                expanded_queries.append("siblings family relationships")
                expanded_queries.append("brothers or sisters")
            elif 'parent' in query.lower() or 'father' in query.lower() or 'mother' in query.lower():
                expanded_queries.append("parents family relationships")
                expanded_queries.append("father and mother")
            elif 'spouse' in query.lower() or 'wife' in query.lower() or 'husband' in query.lower():
                expanded_queries.append("spouse family relationships")
                expanded_queries.append("married to")
        
        return expanded_queries
    
    def _format_conversation_history(self) -> str:
        """
        Format the conversation history for inclusion in the prompt.
        
        Returns:
            Formatted conversation history string
        """
        if not self.conversation_history:
            return ""
        
        formatted_history = "\nPrevious conversation:\n"
        for i, (q, a) in enumerate(self.conversation_history[-5:], 1):  # Include the last 5 exchanges
            formatted_history += f"Question {i}: {q}\n"
            formatted_history += f"Answer {i}: {a}\n\n"
        
        return formatted_history
    
    def clear_history(self) -> None:
        """
        Clear the conversation history.
        """
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_answer(
        self, 
        query: str, 
        k: int = DEFAULT_TOP_K,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        system_prompt: Optional[str] = None  # Not used, here for backward compatibility
    ) -> Tuple[str, List[str]]:
        """
        Get an answer for the query using RAG approach.
        
        Args:
            query: User's question
            k: Number of document chunks to retrieve
            temperature: Temperature parameter for generation
            top_p: Top-p parameter for generation
            max_tokens: Maximum number of tokens to generate
            system_prompt: Not used, here for backward compatibility
            
        Returns:
            Tuple containing the generated answer and the retrieved context chunks
        """
        if not self.vector_store:
            err_msg = "Vector store not initialized"
            logger.error(err_msg)
            raise ValueError(err_msg)
        
        try:
            # Generate expanded queries for better retrieval
            expanded_queries = self._expand_query(query)
            all_contexts = []
            
            # Retrieve relevant document chunks for each expanded query
            for expanded_query in expanded_queries:
                logger.info(f"Retrieving chunks for expanded query: '{expanded_query}'")
                docs = self.vector_store.similarity_search(expanded_query, k=min(k, 3))  # Use fewer chunks per expanded query
                all_contexts.extend([doc.page_content for doc in docs])
            
            # Remove duplicates while preserving order
            seen = set()
            context = [x for x in all_contexts if not (x in seen or seen.add(x))]
            
            # Limit to top k chunks
            context = context[:k]
            
            # Format context in a simple, natural way
            formatted_context = "\n\n".join(context)
            
            # Get formatted conversation history
            conversation_history = self._format_conversation_history()
            
            # Create a prompt that aligns with OLIVER's identity as John's assistant
            prompt = f"""Here's information about John:

{formatted_context}

{conversation_history}
John's query: {query}

IMPORTANT: Respond as OLIVER, John's personal AI assistant. DO NOT refer to "documents", "files", "context", or "information provided". Instead, speak as if you inherently know this information about John. Be consistent with information shared in previous exchanges."""
            
            # Generate response using direct API call to Ollama
            logger.info(f"Generating response with model {self.model}")
            
            # Create the payload for the Ollama API
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens
                }
            }
            
            # Make the API call
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            
            if response.status_code != 200:
                raise Exception(f"Failed to generate response: Status code {response.status_code}, {response.text}")
                
            response_json = response.json()
            answer = response_json['response']
            
            # Update conversation history
            self.conversation_history.append((query, answer))
            # Keep only the last 10 exchanges to avoid context length issues
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            logger.info("Response generated successfully")
            return answer, context
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def reload_vector_store(self) -> None:
        """
        Reload the vector store with the latest markdown content.
        """
        logger.info("Reloading vector store")
        try:
            self._initialize_vector_store()
            logger.info("Vector store reloaded successfully")
        except Exception as e:
            logger.error(f"Error reloading vector store: {e}")
            raise
            
    def set_model(self, model: str) -> None:
        """
        Change the model used by the RAG assistant.
        
        Args:
            model: New model to use
        """
        logger.info(f"Changing model from {self.model} to {model}")
        self.model = model
        
        # Reinitialize the vector store with the new model
        self.reload_vector_store()
