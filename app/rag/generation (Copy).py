import os
import logging
import asyncio
from typing import List
from app.models.schemas import SourceChunk

logger = logging.getLogger(__name__)

# Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "huggingface").lower()
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "microsoft/DialoGPT-medium")  # Better default
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "150"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.9"))
REPETITION_PENALTY = float(os.getenv("REPETITION_PENALTY", "1.1"))

_hf_pipeline = None
_current_model_name = None  # Track which model is loaded

def _load_hf_pipeline():
    """Load the HuggingFace pipeline once and cache it."""
    global _hf_pipeline, _current_model_name
    
    # If model name changed, force reload
    if _current_model_name != HF_MODEL_NAME:
        logger.info(f"Model changed from {_current_model_name} to {HF_MODEL_NAME}, reloading...")
        _hf_pipeline = None
        _current_model_name = None
    
    if _hf_pipeline is None:
        from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
        import torch
        
        # Set custom cache directory
        cache_dir = os.path.join(os.path.dirname(__file__), "..", "models_cache", "llm")
        os.makedirs(cache_dir, exist_ok=True)
        
        logger.info("=" * 60)
        logger.info(f"Loading HuggingFace model: {HF_MODEL_NAME}")
        logger.info(f"Cache directory: {cache_dir}")
        logger.info("=" * 60)
        
        try:
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                HF_MODEL_NAME, 
                cache_dir=cache_dir
            )
            
            # Set padding token if not set
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model with CPU optimization
            model = AutoModelForCausalLM.from_pretrained(
                HF_MODEL_NAME,
                cache_dir=cache_dir,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            _hf_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=-1,  # CPU
                torch_dtype=torch.float32
            )
            
            _current_model_name = HF_MODEL_NAME
            logger.info(f"✅ Model '{HF_MODEL_NAME}' loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load model {HF_MODEL_NAME}: {e}")
            logger.info("Falling back to a smaller model...")
            
            # Fallback to a smaller model
            fallback_model = "microsoft/DialoGPT-small"
            tokenizer = AutoTokenizer.from_pretrained(fallback_model, cache_dir=cache_dir)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            model = AutoModelForCausalLM.from_pretrained(
                fallback_model,
                cache_dir=cache_dir,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            _hf_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=-1
            )
            _current_model_name = fallback_model
            logger.info(f"✅ Fallback model '{fallback_model}' loaded successfully!")
    
    return _hf_pipeline

def build_prompt(question: str, context_chunks: List[SourceChunk]) -> str:
    """Build a better prompt for the model."""
    if not context_chunks:
        return f"""You are a helpful FAQ assistant for Company X, an online EduTech platform.

I don't have specific information about: {question}

Please provide a helpful response suggesting they contact support or check the website."""

    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"Context {i} (from {chunk.source}):\n{chunk.content}"
        )
    context_block = "\n\n".join(context_parts)

    # Improved prompt format for better responses
    prompt = f"""You are a helpful FAQ assistant for Company X, an online EduTech platform.

Use ONLY the context information below to answer questions. If the context doesn't contain the information, say you don't know.

{context_block}

Question: {question}

Provide a clear, concise answer based on the context:"""

    return prompt

def _generate_huggingface(prompt: str) -> str:
    """Generate text using HuggingFace model with better settings."""
    pipe = _load_hf_pipeline()
    
    try:
        logger.debug(f"Generating with model: {_current_model_name}")
        
        # Generate response with better parameters
        outputs = pipe(
            prompt,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            do_sample=True,
            top_p=TOP_P,
            repetition_penalty=REPETITION_PENALTY,
            pad_token_id=pipe.tokenizer.eos_token_id,
            eos_token_id=pipe.tokenizer.eos_token_id,
            no_repeat_ngram_size=3  # Prevent repetition
        )
        
        # Extract generated text
        full_text = outputs[0]["generated_text"]
        
        # Remove the prompt from the response
        if full_text.startswith(prompt):
            answer = full_text[len(prompt):].strip()
        else:
            answer = full_text.strip()
        
        # Clean up the answer
        # Remove any repeated patterns (common in small models)
        lines = answer.split('\n')
        clean_lines = []
        seen = set()
        for line in lines:
            if line.strip() and line.strip() not in seen:
                clean_lines.append(line.strip())
                seen.add(line.strip())
        
        answer = ' '.join(clean_lines)
        
        # Truncate at a reasonable length
        if len(answer) > 500:
            # Find last sentence boundary
            last_period = answer[:500].rfind('.')
            if last_period > 100:
                answer = answer[:last_period + 1]
        
        # Check if answer is too short or empty
        # if not answer or len(answer) < 15:
        #     return "I'm sorry, I don't have enough information to answer that question."
        
        return answer
        
    except Exception as e:
        logger.error(f"HuggingFace generation failed: {e}")
        return "I'm sorry, I encountered an error while generating the answer."

async def generate_answer(
    question: str,
    context_chunks: List[SourceChunk],
) -> str:
    """Generate an answer using the LLM."""
    
    # Handle empty question
    if not question or not question.strip():
        return "Please provide a question to answer."
    
    # If no relevant context found
    if not context_chunks:
        return (
            "I'm sorry, I couldn't find any relevant information about your question. "
            "Please contact our support team at support@companyx.edu for assistance."
        )
    
    # Check if context has low relevance scores
    if context_chunks and context_chunks[0].score < 0.3:
        return (
            "I found some potentially relevant information, but I'm not confident it matches your question. "
            "Please try rephrasing your question or contact support for more accurate information."
        )
    
    prompt = build_prompt(question, context_chunks)
    loop = asyncio.get_event_loop()
    
    logger.debug("Generating with HuggingFace model '%s'", HF_MODEL_NAME)
    answer = await loop.run_in_executor(None, _generate_huggingface, prompt)
    
    # Final cleanup: ensure answer is reasonable
    if len(answer) < 10:
        return "I'm sorry, I couldn't generate a proper answer. Please try asking differently."
    
    return answer

def get_model_name() -> str:
    """Return the actual model being used."""
    if _current_model_name:
        return f"huggingface/{_current_model_name}"
    return f"huggingface/{HF_MODEL_NAME}"