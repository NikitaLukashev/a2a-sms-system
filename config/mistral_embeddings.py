"""
Custom Mistral Embeddings for LangChain
Uses Mistral AI API for generating embeddings
"""

import os
import logging
from typing import List, Union
from mistralai.client import MistralClient
from langchain.embeddings.base import Embeddings

logger = logging.getLogger(__name__)

class MistralEmbeddings(Embeddings):
    """Custom Mistral embeddings using Mistral AI API"""
    
    def __init__(self, model: str = "mistral-embed", api_key: str = None):
        """
        Initialize Mistral embeddings
        
        Args:
            model: Mistral embedding model name (default: mistral-embed)
            api_key: Mistral API key (defaults to MISTRAL_API_KEY env var)
        """
        self.model = model
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        
        if not self.api_key:
            raise ValueError("Mistral API key is required. Set MISTRAL_API_KEY environment variable.")
        
        self.client = MistralClient(api_key=self.api_key)
        logger.info(f"Mistral embeddings initialized with model: {self.model}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents using Mistral AI
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            # Generate embedding for single text
            response = self.client.embeddings(
                model=self.model,
                input=text
            )
            embedding = response.data[0].embedding
            embeddings.append(embedding)
        
        logger.info(f"Generated embeddings for {len(texts)} documents")
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text using Mistral AI
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        response = self.client.embeddings(
            model=self.model,
            input=text
        )
        embedding = response.data[0].embedding
        logger.info(f"Generated embedding for query: {text[:50]}...")
        return embedding
