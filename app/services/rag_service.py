"""RAG (Retrieval-Augmented Generation) service."""
import logging
from typing import List, Tuple
from app.services.vector_store import VectorStore
from app.services.chunking import chunk_text
from app.services.llm_service import LLMService
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based chatbot."""
    
    def __init__(self):
        """Initialize RAG service."""
        self.vector_store = VectorStore(settings.embedding_model)
        self.llm_service = LLMService()
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.top_k = settings.top_k_retrieval
        self.similarity_threshold = settings.similarity_threshold
    
    def index_documents(self, documents: List[str]) -> int:
        """Index documents in the vector store.
        
        Args:
            documents: List of document texts to index
            
        Returns:
            Number of chunks indexed
        """
        logger.info(f"Starting indexing of {len(documents)} documents")
        
        # Chunk documents
        all_chunks = []
        for doc in documents:
            chunks = chunk_text(doc, self.chunk_size, self.chunk_overlap)
            all_chunks.extend(chunks)
        
        # Add to vector store
        if all_chunks:
            self.vector_store.add_documents(all_chunks)
            logger.info(f"Successfully indexed {len(all_chunks)} chunks")
        else:
            logger.warning("No chunks created from documents")
        
        return len(all_chunks)
    
    def retrieve(self, query: str) -> List[Tuple[str, float]]:
        """Retrieve relevant documents from the knowledge base.
        
        Args:
            query: User query
            
        Returns:
            List of (document, similarity_score) tuples
        """
        if self.vector_store.is_empty():
            logger.warning("Vector store is empty, returning empty results")
            return []
        
        results = self.vector_store.search(query, top_k=self.top_k)
        
        # Filter by similarity threshold
        filtered_results = [
            (doc, score) for doc, score in results 
            if score >= self.similarity_threshold
        ]
        
        logger.debug(f"Retrieved {len(filtered_results)} documents for query: {query}")
        return filtered_results
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate answer using LLM.
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        logger.debug(f"Generating answer for query: {query}")
        answer = self.llm_service.generate(query, context)
        return answer
    
    # Common greetings and chitchat patterns
    _GREETINGS = {
        "hi", "hello", "hey", "howdy", "hiya", "yo", "sup",
        "good morning", "good afternoon", "good evening", "good day",
        "hi there", "hello there", "hey there",
    }

    def _is_greeting(self, query: str) -> bool:
        """Return True if the query is a simple greeting or chitchat."""
        normalised = query.strip().lower().rstrip("!.,?")
        return normalised in self._GREETINGS

    def answer_question(self, query: str) -> Tuple[str, List[str], float]:
        """Answer a user question using RAG pipeline.
        
        Args:
            query: User question
            
        Returns:
            Tuple of (answer, sources, confidence_score)
        """
        logger.info(f"Processing query: {query}")

        # Handle greetings before touching the knowledge base
        if self._is_greeting(query):
            return (
                "Hello! 👋 Welcome to Academy X. I'm here to help you with any questions "
                "about our tech training programs, enrollment, fees, policies, and support. "
                "What would you like to know?",
                [],
                1.0,
            )

        # Step 1: Retrieve relevant documents
        retrieved_docs = self.retrieve(query)

        if not retrieved_docs:
            logger.warning(f"No relevant documents found for query: {query}")
            return (
                "I don't have specific information about that in my knowledge base right now. "
                "You're welcome to ask about our courses, enrollment process, fees, policies, or support — "
                "or reach out to us directly at support@academyx.abc and we'll be happy to help! 😊",
                [],
                0.0,
            )
        
        # Step 2: Prepare context from retrieved documents
        context = self._prepare_context(retrieved_docs)
        sources = [doc for doc, _ in retrieved_docs]
        
        # Calculate average confidence
        avg_confidence = sum(score for _, score in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0.0
        
        # Step 3: Generate answer
        answer = self.generate_answer(query, context)
        
        logger.info(f"Generated answer with confidence: {avg_confidence:.2f}")
        
        return answer, sources, avg_confidence
    
    def _prepare_context(self, documents: List[Tuple[str, float]]) -> str:
        """Prepare context string from retrieved documents.
        
        Args:
            documents: List of (document, score) tuples
            
        Returns:
            Formatted context string
        """
        context_parts = []
        for i, (doc, score) in enumerate(documents, 1):
            context_parts.append(f"[Document {i} - Relevance: {score:.2f}]\n{doc}")
        
        return "\n\n".join(context_parts)
    
    def save_index(self, path: str):
        """Save the vector store index to disk.
        
        Args:
            path: Path to save the index
        """
        self.vector_store.save(path)
        logger.info(f"Index saved to {path}")
    
    def load_index(self, path: str):
        """Load the vector store index from disk.
        
        Args:
            path: Path to load the index from
        """
        self.vector_store.load(path)
        logger.info(f"Index loaded from {path}")
    
    def is_indexed(self) -> bool:
        """Check if the vector store has indexed documents."""
        return not self.vector_store.is_empty()
    
    def get_document_count(self) -> int:
        """Get the number of indexed documents."""
        return len(self.vector_store.documents)
