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
        self._is_chat_model = False
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
        """Setup Hugging Face LLM via direct Inference API (Python 3.14 compatible)."""
        if not settings.hf_api_token:
            logger.warning("No HF_API_TOKEN configured; falling back to mock LLM")
            self._setup_mock()
            return
        try:
            self.llm = _HFInferenceLLM(
                model=settings.hf_model_name,
                token=settings.hf_api_token,
                max_new_tokens=256,
                temperature=0.7,
            )
            self._is_chat_model = False
            logger.info(f"Hugging Face Inference API initialized ({settings.hf_model_name})")
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
            response = self.llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            return text.strip() if text else "I could not generate a response."
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
        prompt = f"""You are a friendly and knowledgeable support assistant for Academy X, a tech training hub that offers practical, industry-focused technology programs.
Your job is to help prospective and current trainees by answering their questions clearly and conversationally.

Guidelines:
- Answer in your own words — do NOT copy the context verbatim
- Be concise but complete; use bullet points only when listing 3 or more items
- If the context does not contain enough information, say so honestly and suggest contacting the admissions team
- Never mention universities, degrees, GPA, SAT scores, or traditional academic language
- Maintain a warm, encouraging tone suited to someone exploring a career in tech

Context (internal knowledge base — do not quote directly):
{context}

Trainee Question: {query}

Assistant:"""
        return prompt


class _HFInferenceLLM:
    """Wrapper around huggingface_hub.InferenceClient using chat_completion.

    Uses the new HF router (router.huggingface.co) via chat_completion which
    is fully compatible with Python 3.14 and the current HF Inference API.
    """

    def __init__(self, model: str, token: str, max_new_tokens: int = 256, temperature: float = 0.7):
        from huggingface_hub import InferenceClient  # type: ignore
        self.client = InferenceClient(model=model, token=token)
        self.model = model
        self.max_tokens = max_new_tokens
        self.temperature = temperature

    def invoke(self, prompt: str) -> str:
        result = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return result.choices[0].message.content or ""

    def __call__(self, prompt: str) -> str:
        return self.invoke(prompt)


class MockLLM:
    """Mock LLM for testing when real LLM is not available."""

    def invoke(self, prompt: str) -> str:
        """Generate mock response."""
        if "admission" in prompt.lower():
            return "Thank you for your question about admissions. Please visit our admissions portal or contact our admissions office for detailed information about application requirements and timelines."
        elif "fee" in prompt.lower() or "cost" in prompt.lower():
            return "For information about course fees, please check our pricing page or contact our finance department for detailed breakdowns."
        elif "course" in prompt.lower():
            return "We offer a variety of courses designed to enhance your skills. Please visit our course catalog for detailed descriptions and prerequisites."
        else:
            return "Thank you for your question. Based on our knowledge base, we recommend visiting our FAQ section or contacting our support team for more specific information."

    def __call__(self, prompt: str) -> str:
        return self.invoke(prompt)
