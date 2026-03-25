import requests
import json

BASE = "http://127.0.0.1:8000"

def test_endpoint(name, question):
    print(f"\n{'='*50}")
    print(f"🧪 Testing: {name}")
    print(f"Q: {question}")
    
    try:
        resp = requests.post(f"{BASE}/api/chat", json={"question": question})
        
        if resp.status_code != 200:
            print(f"❌ Error: {resp.status_code} - {resp.text}")
            return None
            
        data = resp.json()
        
        print(f"A: {data['answer']}")
        print(f"📚 Sources: {len(data['sources'])} chunks")
        if data['sources']:
            print(f"📄 Top source: {data['sources'][0]['source']} (score: {data['sources'][0]['score']:.3f})")
        print(f"🤖 Model: {data['model_used']}")
        return data
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

# Run tests
print("🚀 Company X RAG Bot - Final Tests\n")

# Test basic questions
test_endpoint("Courses", "What courses are available?")
test_endpoint("Pricing", "How much does Web Development cost?")
test_endpoint("Refund", "What is the refund policy?")
test_endpoint("Support", "How do I contact support?")

# Test edge cases
test_endpoint("No info", "What is the CEO's name?")
test_endpoint("Empty query", " ")
