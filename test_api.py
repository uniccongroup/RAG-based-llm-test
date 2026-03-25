#!/usr/bin/env python
"""Integration tests for RAG chatbot API."""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n📋 Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print(f"✓ Health check passed: {data['message']}")


def test_index_status():
    """Test index status endpoint."""
    print("\n📊 Testing Index Status...")
    response = requests.get(f"{BASE_URL}/api/index-status")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Index Status: {data['message']}")
    print(f"  - Indexed: {data['indexed']}")
    print(f"  - Document Count: {data['document_count']}")
    return data['indexed']


def test_chat(queries):
    """Test chat endpoint with various queries."""
    print("\n💬 Testing Chat Endpoint...")
    
    for query in queries:
        print(f"\n  Query: '{query}'")
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"query": query}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"  Answer: {data['answer'][:100]}...")
        print(f"  Confidence: {data['confidence']:.2f}")
        print(f"  Sources: {len(data['sources'])} document(s)")
        
        # Validate response structure
        assert "query" in data
        assert "answer" in data
        assert "sources" in data
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1


def test_document_upload():
    """Test document upload endpoint."""
    print("\n📤 Testing Document Upload...")
    
    # Create a test file
    test_content = """
    Q: What is the best programming language?
    A: The best language depends on your use case. Python is great for data science,
    JavaScript for web development, and Rust for systems programming.
    
    Q: How long does it take to learn programming?
    A: Basic programming concepts take 2-4 weeks of dedicated study.
    Becoming proficient takes 3-6 months of practice.
    """
    
    test_file = Path("test_document.txt")
    test_file.write_text(test_content)
    
    try:
        with open(test_file, "rb") as f:
            files = {"files": f}
            response = requests.post(
                f"{BASE_URL}/api/upload-documents",
                files=files
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"✓ Upload successful")
        print(f"  - Documents: {data['document_count']}")
        print(f"  - Chunks: {data['chunk_count']}")
    
    finally:
        # Cleanup
        test_file.unlink(missing_ok=True)


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("🧪 RAG Chatbot Integration Tests")
    print("=" * 60)
    
    try:
        # Test health
        test_health()
        
        # Test index status
        is_indexed = test_index_status()
        
        if not is_indexed:
            print("\n⚠️  Knowledge base not indexed. Initializing...")
            import subprocess
            subprocess.run(["python", "setup_kb.py"], check=True)
            time.sleep(2)
        
        # Test chat with sample queries
        test_queries = [
            "What are the admission requirements?",
            "How much is tuition?",
            "Are online courses available?",
            "What health services are available?"
        ]
        test_chat(test_queries)
        
        # Test document upload
        test_document_upload()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server")
        print("   Make sure the server is running: python run.py")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
