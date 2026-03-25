import os
from pathlib import Path

# Set cache paths
cache_dir = Path("app/models_cache")
embeddings_dir = cache_dir / "embeddings"
llm_dir = cache_dir / "llm"

embeddings_dir.mkdir(parents=True, exist_ok=True)
llm_dir.mkdir(parents=True, exist_ok=True)

print("📥 Downloading embedding model (all-MiniLM-L6-v2)...")
from sentence_transformers import SentenceTransformer
embed_model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    cache_folder=str(embeddings_dir)
)
print("✅ Embedding model downloaded\n")

print("📥 Downloading LLM (distilgpt2)...")
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "distilgpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=str(llm_dir))
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=str(llm_dir))
print("✅ LLM downloaded\n")

print("🎉 All models downloaded to app/models_cache/")
print(f"   - Embeddings: {embeddings_dir} (80MB)")
print(f"   - LLM: {llm_dir} (82MB)")
print(f"   - Total: ~162MB")
