"""
Core RAG assistant functionality that retrieves relevant information and
augments LLM responses.
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Union

import ollama
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings


class RAGAssistant:
    """
    Retrieval Augmented Generation Assistant that enhances LLM responses
    with retrieved information from personal markdown documents.
    """
    
    def __init__(self, markdown_file: str, model: str = "mistral"):
        """
        Initialize the RAG Assistant.
        
        Args:
            markdown_file: Path to the markdown file with personal information
            model: Ollama model to use for embeddings and generation
        """
        self.model = model
        self.markdown_file = markdown_file
        self.vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self) -> None:
        """
        Initialize the vector store with chunks from the markdown file.
        """
        if not os.path.exists(self.markdown_file):
            raise FileNotFoundError(f"Markdown file not found: {self.markdown_file}")
            
        with open(self.markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Split markdown into chunks
        markdown_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = markdown_splitter.split_text(markdown_content)
        
        # Create vector store
        embeddings = OllamaEmbeddings(model=self.model)
        self.vector_store = FAISS.from_texts(chunks, embeddings)
    
    def get_answer(self, query: str, k: int = 3) -> Tuple[str, List[str]]:
        """
        Get an answer for the query using RAG approach.
        
        Args:
            query: User's question
            k: Number of document chunks to retrieve
            
        Returns:
            Tuple containing the generated answer and the retrieved context chunks
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
            
        # Retrieve relevant document chunks
        docs = self.vector_store.similarity_search(query, k=k)
        context = [doc.page_content for doc in docs]
        
        # Format context and query for the model
        formatted_context = "\n\n".join(context)
        prompt = (
            "You are a helpful assistant that provides accurate information based on the "
            "following personal information. Respond in a friendly, conversational way. "
            "If you don't know the answer, say so.\n\n"
            f"PERSONAL INFORMATION:\n{formatted_context}\n\n"
            f"QUESTION: {query}\n\n"
            "ANSWER:"
        )
        
        # Generate response using ollama
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": 0.7}
        )
        
        return response['response'], context

    def reload_vector_store(self) -> None:
        """
        Reload the vector store with the latest markdown content.
        """
        self._initialize_vector_store()
