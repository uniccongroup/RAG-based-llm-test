import os
import logging
import asyncio
from typing import List
from app.models.schemas import SourceChunk

logger = logging.getLogger(__name__)

# Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "huggingface").lower()
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "gpt2-medium")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "80"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
TOP_P = float(os.getenv("TOP_P", "0.85"))
REPETITION_PENALTY = float(os.getenv("REPETITION_PENALTY", "1.3"))

_hf_pipeline = None
_current_model_name = None

def _load_hf_pipeline():
    """Load the HuggingFace pipeline once and cache it."""
    global _hf_pipeline, _current_model_name
    
    if _current_model_name != HF_MODEL_NAME:
        logger.info(f"Loading model: {HF_MODEL_NAME}...")
        _hf_pipeline = None
        _current_model_name = None
    
    if _hf_pipeline is None:
        from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
        
        cache_dir = os.path.join(os.path.dirname(__file__), "..", "models_cache", "llm")
        os.makedirs(cache_dir, exist_ok=True)
        
        logger.info(f"Loading {HF_MODEL_NAME}...")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME, cache_dir=cache_dir)
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                HF_MODEL_NAME,
                cache_dir=cache_dir,
                low_cpu_mem_usage=True
            )
            
            _hf_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=-1
            )
            
            _current_model_name = HF_MODEL_NAME
            logger.info(f"✅ Model loaded: {HF_MODEL_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to load {HF_MODEL_NAME}: {e}")
            raise
    
    return _hf_pipeline

def build_prompt(question: str, context_chunks: List[SourceChunk]) -> str:
    """Build a concise prompt that encourages short answers."""
    if not context_chunks:
        return f"""Question: {question}
Answer: I don't have that information."""

    # Build context with only the most relevant chunks
    context_section = "\n".join([f"- {chunk.content}" for chunk in context_chunks[:2]])  # Use top 2 chunks only
    
    # Simplified prompt that encourages direct answers
    prompt = f"""Based on this information:
{context_section}

Question: {question}
Answer (be concise):"""
    
    return prompt

def clean_generated_text(text: str, question: str) -> str:
    """Clean up generated text to get a concise answer."""
    # Remove any repetition of the question
    if question.lower() in text.lower():
        text = text.split("Answer:")[-1] if "Answer:" in text else text
    
    # Take only the first sentence or two
    sentences = text.split('.')
    if len(sentences) > 1:
        # Take first sentence that has meaningful length
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and len(sentence) < 200:
                text = sentence + '.'
                break
    
    # Remove common filler words at the start
    text = text.lstrip("Answer: ").lstrip("Based on this information: ").strip()
    
    # Remove emojis if any
    import re
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Ensure answer is concise
    if len(text) > 150:
        # Try to cut at last period
        last_period = text[:150].rfind('.')
        if last_period > 50:
            text = text[:last_period + 1]
    
    return text

def _generate_huggingface(prompt: str, question: str) -> str:
    """Generate text with better parameters to avoid repetition."""
    pipe = _load_hf_pipeline()
    
    try:
        outputs = pipe(
            prompt,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            do_sample=True,
            top_p=TOP_P,
            repetition_penalty=REPETITION_PENALTY,
            pad_token_id=pipe.tokenizer.eos_token_id,
            no_repeat_ngram_size=3,
            early_stopping=True  # Stop when answer seems complete
        )
        
        full_text = outputs[0]["generated_text"]
        
        # Extract answer (everything after the prompt)
        if full_text.startswith(prompt):
            answer = full_text[len(prompt):].strip()
        else:
            answer = full_text.strip()
        
        # Clean up
        answer = clean_generated_text(answer, question)
        
        # Check for meaningful answer
        if not answer or len(answer) < 5:
            return "I don't have that information."
        
        # Check if answer is just repeating itself
        words = answer.split()
        if len(words) > 15 and len(set(words)) < 8:
            # Too repetitive, fall back to a simple answer
            return "Please refer to our documentation for more details."
        
        return answer
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return "I encountered an error while generating the answer."

async def generate_answer(
    question: str,
    context_chunks: List[SourceChunk],
) -> str:
    """Generate an answer using the LLM."""
    
    if not question or not question.strip():
        return "Please provide a question to answer."
    
    if not context_chunks:
        return "I couldn't find relevant information. Please contact support@companyx.edu for help."
    
    # If the top result has low relevance, add a disclaimer
    low_relevance = context_chunks[0].score < 0.35
    
    prompt = build_prompt(question, context_chunks)
    loop = asyncio.get_event_loop()
    
    answer = await loop.run_in_executor(None, _generate_huggingface, prompt, question)
    
    # Add disclaimer for low relevance answers
    if low_relevance and not answer.startswith("I don't have"):
        answer = f"Based on available information: {answer}"
    
    return answer

def get_model_name() -> str:
    return f"huggingface/{_current_model_name or HF_MODEL_NAME}"