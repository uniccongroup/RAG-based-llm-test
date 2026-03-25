import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("🔍 Testing Health...")
    resp = requests.get(f"{BASE_URL}/health")
    data = resp.json()
    print(f"   Status: {data['status']}")
    print(f"   Vector Store: {'✅ Loaded' if data['vector_store_loaded'] else '❌ Empty'}")
    print(f"   Chunks: {data['total_chunks']}")
    print(f"   Model: {data['model']}")
    return data['vector_store_loaded']

def test_chat(question):
    print(f"\n💬 Question: {question}")
    resp = requests.post(
        f"{BASE_URL}/api/chat",
        json={"question": question, "top_k": 3}
    )
    data = resp.json()
    print(f"   Answer: {data['answer'][:200]}...")
    print(f"   Sources: {len(data['sources'])} chunks retrieved")
    if data['sources']:
        print(f"   Top source: {data['sources'][0]['source']} (score: {data['sources'][0]['score']})")
    return data

# Run tests
if __name__ == "__main__":
    if test_health():
        test_chat("What courses does Company X offer?")
        test_chat("What is your refund policy?")
        test_chat("How can I contact support?")
        test_chat("What's the price for Web Development?")
    else:
        print("\n⚠️ Vector store not loaded! Run: POST /api/ingest")
