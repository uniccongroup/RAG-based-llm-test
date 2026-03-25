"""Language Model Integration Service."""
import logging
from typing import Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM integration."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.provider = settings.llm_provider
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM based on provider."""
        try:
            if self.provider == "huggingface":
                self._setup_huggingface()
            elif self.provider == "openai":
                self._setup_openai()
            elif self.provider == "cohere":
                self._setup_cohere()
            else:
                logger.warning(f"Unknown LLM provider: {self.provider}, using Hugging Face")
                self._setup_huggingface()
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            # Fallback to mock LLM
            self._setup_mock()
    
    def _setup_huggingface(self):
        """Setup Hugging Face LLM via Inference API."""
        if not settings.hf_api_token:
            logger.warning("No HF_API_TOKEN configured; falling back to mock LLM")
            self._setup_mock()
            return
        try:
            # Prefer the maintained langchain-huggingface package
            try:
                from langchain_huggingface import HuggingFaceEndpoint  # type: ignore
                self.llm = HuggingFaceEndpoint(
                    repo_id=settings.hf_model_name,
                    huggingfacehub_api_token=settings.hf_api_token,
                    max_new_tokens=256,
                    temperature=0.7,
                )
            except ImportError:
                # Fallback to langchain_community
                from langchain_community.llms import HuggingFaceHub  # type: ignore
                self.llm = HuggingFaceHub(
                    repo_id=settings.hf_model_name,
                    huggingfacehub_api_token=settings.hf_api_token,
                    model_kwargs={"max_new_tokens": 256, "temperature": 0.7},
                )
            logger.info("Hugging Face LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to setup Hugging Face LLM: {e}")
            self._setup_mock()
    
    def _setup_openai(self):
        """Setup OpenAI LLM."""
        try:
            from langchain_community.llms import OpenAI
            
            self.llm = OpenAI(
                api_key=settings.openai_api_key,
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=256
            )
            logger.info("OpenAI LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to setup OpenAI LLM: {e}")
            self._setup_mock()
    
    def _setup_cohere(self):
        """Setup Cohere LLM."""
        try:
            from langchain_community.llms import Cohere
            
            self.llm = Cohere(
                cohere_api_key=settings.cohere_api_key,
                model="command",
                temperature=0.7,
                max_tokens=256
            )
            logger.info("Cohere LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to setup Cohere LLM: {e}")
            self._setup_mock()
    
    def _setup_mock(self):
        """Setup mock LLM for testing."""
        logger.info("Using mock LLM for testing")
        self.llm = MockLLM()
    
    def generate(self, query: str, context: str) -> str:
        """Generate response using LLM.
        
        Args:
            query: User query
            context: Retrieved context from knowledge base
            
        Returns:
            Generated response
        """
        if self.llm is None:
            return "LLM service is not available"
        
        try:
            prompt = self._build_prompt(query, context)
            response = self.llm(prompt)
            return response.strip() if response else "I could not generate a response."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build the prompt for the LLM.
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful FAQ assistant for Company X, an Edu-Tech organization.
Use the provided context to answer the user's question accurately and concisely.

Context:
{context}

User Question: {query}

Answer:"""
        return prompt


class MockLLM:
    """Mock LLM for testing when real LLM is not available."""
    
    def __call__(self, prompt: str) -> str:
        """Generate mock response."""
        if "admission" in prompt.lower():
            return "Thank you for your question about admissions. Please visit our admissions portal or contact our admissions office for detailed information about application requirements and timelines."
        elif "fee" in prompt.lower() or "cost" in prompt.lower():
            return "For information about course fees, please check our pricing page or contact our finance department for detailed breakdowns."
        elif "course" in prompt.lower():
            return "We offer a variety of courses designed to enhance your skills. Please visit our course catalog for detailed descriptions and prerequisites."
        else:
            return "Thank you for your question. Based on our knowledge base, we recommend visiting our FAQ section or contacting our support team for more specific information."
