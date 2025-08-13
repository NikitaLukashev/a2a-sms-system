"""
RAG-based Property Information Parser for SMS Host Protocol
Uses LangChain and vector database for intelligent information retrieval
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from .mistral_embeddings import MistralEmbeddings

# Configure logging
logger = logging.getLogger(__name__)

class RAGPropertyParser:
    """RAG-based property information parser using LangChain and vector database"""
    
    def __init__(self, data_directory: str = "data", persist_directory: str = None):
        # Use absolute paths to avoid permission issues
        self.data_directory = Path(data_directory).resolve()
        
        # Set persist directory based on environment
        if persist_directory is None:
            # Check if we're in Docker (PYTHONPATH will be /app)
            if os.getenv('PYTHONPATH') == '/app':
                # Docker environment - use /app/vector_db
                self.persist_directory = Path('/app/vector_db')
            else:
                # Local environment - use project root
                project_root = Path(__file__).parent.parent
                self.persist_directory = project_root / "vector_db"
        else:
            self.persist_directory = Path(persist_directory).resolve()
        
        self.vector_store = None
        self.embeddings = None
        self.text_splitter = None
        
        # Initialize components
        self._initialize_components()
        
        # Load or create vector database
        self._setup_vector_database()
    
    def _initialize_components(self):
        """Initialize LangChain components"""
        # Initialize text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize Mistral embeddings model
        self.embeddings = MistralEmbeddings(
            model="mistral-embed",
            api_key=os.getenv("MISTRAL_API_KEY")
        )
        
        logger.info("LangChain components initialized successfully with Mistral embeddings")
    
    def _setup_vector_database(self):
        """Setup or load the vector database"""
        try:
            # Create persist directory if it doesn't exist
            self.persist_directory.mkdir(exist_ok=True, parents=True)
            
            # Ensure the directory has proper permissions
            self.persist_directory.chmod(0o755)
            
            logger.info(f"Vector database directory: {self.persist_directory}")
            logger.info(f"Directory permissions: {oct(self.persist_directory.stat().st_mode)[-3:]}")
            
            # Check if vector database already exists
            if (self.persist_directory / "chroma.sqlite3").exists():
                logger.info("Loading existing vector database...")
                self.vector_store = Chroma(
                    persist_directory=str(self.persist_directory),
                    embedding_function=self.embeddings
                )
            else:
                logger.info("Creating new vector database...")
                self._create_vector_database()
                
            logger.info("Vector database setup completed")
            
        except PermissionError as e:
            logger.error(f"Permission error creating vector database: {e}")
            logger.error(f"Directory: {self.persist_directory}")
            logger.error(f"Current working directory: {Path.cwd()}")
            raise
        except Exception as e:
            logger.error(f"Error setting up vector database: {e}")
            raise
    
    def _create_vector_database(self):
        """Create and populate the vector database"""
        # Collect all text files from data directory
        documents = self._collect_documents()
        
        if not documents:
            logger.warning("No documents found in data directory")
            # Create default document
            documents = [self._create_default_document()]
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} text chunks from {len(documents)} documents")
        
        # Create vector store
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(self.persist_directory)
        )
        
        # Persist the database (Chroma 0.4.x automatically persists)
        logger.info("Vector database created and persisted successfully")
    
    def _collect_documents(self) -> List[Document]:
        """Collect all text documents from the data directory"""
        documents = []
        
        # Get all text files from data directory
        text_files = list(self.data_directory.glob("*.txt"))
        
        for file_path in text_files:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Create LangChain Document
            doc = Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "filename": file_path.name,
                    "file_type": "text"
                }
            )
            documents.append(doc)
        
        logger.info(f"Collected {len(documents)} documents from data directory")
        return documents
    
    def _create_default_document(self) -> Document:
        """Create a default document if no data files are found"""
        default_content = """
        PROPERTY NAME: Your Property
        LOCATION: Your City, State
        
        CHECK-IN & CHECK-OUT:
        Check-in time: 3:00 PM
        Check-out time: 11:00 AM
        
        AMENITIES:
        WiFi, Kitchen, Parking, Bathrooms, Bedrooms
        
        HOUSE RULES:
        No smoking, No pets, Quiet hours 10 PM-8 AM
        
        WHAT'S INCLUDED:
        Towels, linens, coffee, tea
        
        NEARBY ATTRACTIONS:
        Restaurants, shopping, attractions
        
        CANCELLATION POLICY:
        Flexible cancellation policy
        """
        
        return Document(
            page_content=default_content,
            metadata={
                "source": "default",
                "filename": "default_property_info.txt",
                "file_type": "text"
            }
        )
    
    def query_property_info(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Query the vector database for relevant property information
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return []
        
        # Perform similarity search
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score),
                "source": doc.metadata.get("source", "unknown")
            })
        
        logger.info(f"Retrieved {len(formatted_results)} relevant chunks for query: '{query}'")
        return formatted_results
    
    def get_property_summary(self) -> str:
        """Get a summary of the property information"""
        # Query for general property information
        results = self.query_property_info("property name location amenities check-in check-out", k=5)
        
        if not results:
            return "Property information not available"
        
        # Extract key information from results
        summary_parts = []
        
        for result in results:
            content = result["content"]
            # Look for key information patterns
            if "property" in content.lower() or "name" in content.lower():
                summary_parts.append(f"🏠 {content.strip()}")
            elif "location" in content.lower() or "metro" in content.lower():
                summary_parts.append(f"📍 {content.strip()}")
            elif "check" in content.lower() and ("pm" in content.lower() or "am" in content.lower()):
                summary_parts.append(f"⏰ {content.strip()}")
            elif "wifi" in content.lower() or "amenity" in content.lower():
                summary_parts.append(f"✨ {content.strip()}")
        
        if summary_parts:
            return "\n".join(summary_parts[:3])  # Limit to 3 key points
        else:
            return "🏠 Your Property\n📍 Location information available\n✨ Amenities and details provided"
    
    def get_specific_info(self, category: str) -> str:
        """
        Get specific information about a category
        
        Args:
            category: The category to search for (e.g., 'wifi', 'check-in', 'parking')
            
        Returns:
            Relevant information about the category
        """
        results = self.query_property_info(category, k=2)
        
        if not results:
            return f"Information about {category} not found"
        
        # Return the most relevant result
        return results[0]["content"].strip()
    
    def format_for_ai_context(self, query: str = None) -> str:
        """
        Format property data for AI context, optionally based on a specific query
        
        Args:
            query: Optional specific query to focus the context
            
        Returns:
            Formatted context for AI
        """
        if query:
            # Get context specific to the query
            results = self.query_property_info(query, k=3)
            if results:
                context_parts = [f"Relevant Property Information for '{query}':"]
                for i, result in enumerate(results, 1):
                    context_parts.append(f"{i}. {result['content'].strip()}")
                return "\n\n".join(context_parts)
        
        # Get general property context
        results = self.query_property_info("property overview amenities location", k=4)
        
        if not results:
            return "Property information not available"
        
        context_parts = ["Property Information:"]
        for i, result in enumerate(results, 1):
            context_parts.append(f"{i}. {result['content'].strip()}")
        
        return "\n\n".join(context_parts)
    
    def refresh_database(self):
        """Refresh the vector database with current data files"""
        logger.info("Refreshing vector database...")
        
        # Remove existing database
        import shutil
        if self.persist_directory.exists():
            shutil.rmtree(self.persist_directory)
        
        # Recreate database
        self._setup_vector_database()
        
        logger.info("Vector database refreshed successfully")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        if not self.vector_store:
            return {"error": "Vector store not initialized"}
        
        # Get collection info
        collection = self.vector_store._collection
        count = collection.count()
        
        return {
            "total_documents": count,
            "data_directory": str(self.data_directory),
            "persist_directory": str(self.persist_directory),
            "embedding_model": "mistral-embed",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "embedding_provider": "Mistral"
        }


# Global instance
property_parser = RAGPropertyParser()
