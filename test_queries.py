"""
Comprehensive Test Suite for Agriculture Chatbot
Tests all three intent types with sample queries from the requirements
"""

import requests
import json
from typing import Dict

BASE_URL = "http://localhost:8000"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_result(query: str, result: Dict):
    """Pretty print test results"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Query:{Colors.ENDC} {query}")
    print(f"{Colors.OKBLUE}Intent:{Colors.ENDC} {result.get('intent', 'N/A')}")
    print(f"\n{Colors.OKGREEN}Answer:{Colors.ENDC}")
    print(result.get('answer', 'No answer')[:500] + "...")
    
    if result.get('sources'):
        print(f"\n{Colors.OKCYAN}Sources:{Colors.ENDC}")
        for source in result['sources'][:3]:
            print(f"  - {source.get('source', 'Unknown')} (Page {source.get('page', 'N/A')})")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")

def test_endpoint(endpoint: str, data: Dict = None):
    """Test a specific endpoint"""
    try:
        if data:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}")
        
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Test Queries organized by intent
TEST_QUERIES = {
    "disease": [
        "My citrus leaves are showing yellow blotchy patches. What could this be?",
        "How do I prevent Citrus Canker in my orchard?",
        "What treatment should I use for whitefly infestation on my citrus trees?"
    ],
    "scheme": [
        "What government schemes are available for citrus farmers in Andhra Pradesh?",
        "Are there any subsidies for setting up drip irrigation in my citrus farm?",
        "How can I get financial help to start organic citrus farming?"
    ],
    "hybrid": [
        "What government schemes can help me manage Citrus Greening disease in my farm?",
        "I need help with pest control equipment and funding. What options do I have?",
        "Can I get government support for setting up drip irrigation to prevent root diseases?"
    ]
}

def main():
    """Run comprehensive test suite"""
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}🌾 Agriculture Chatbot - Test Suite{Colors.ENDC}\n")
    
    # 1. Health Check
    print(f"{Colors.BOLD}1. Testing Health Endpoint...{Colors.ENDC}")
    health = test_endpoint("/health")
    if health.get("status") == "healthy":
        print(f"{Colors.OKGREEN}✓ System is healthy{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✗ System health check failed{Colors.ENDC}")
        return
    
    # 2. Stats Check
    print(f"\n{Colors.BOLD}2. Testing Stats Endpoint...{Colors.ENDC}")
    stats = test_endpoint("/stats")
    print(f"  Total Documents: {stats.get('total_documents', 'N/A')}")
    print(f"  Vector Stores: {list(stats.get('vector_stores', {}).keys())}")
    
    # 3. Test Disease Intent Queries
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}3. Testing DISEASE Intent Queries{Colors.ENDC}")
    for query in TEST_QUERIES["disease"]:
        result = test_endpoint("/query", {"question": query})
        print_result(query, result)
        
        # Verify intent
        if result.get("intent") == "disease":
            print(f"{Colors.OKGREEN}✓ Intent correctly detected{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠ Intent mismatch: expected 'disease', got '{result.get('intent')}'{Colors.ENDC}")
    
    # 4. Test Scheme Intent Queries
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}4. Testing SCHEME Intent Queries{Colors.ENDC}")
    for query in TEST_QUERIES["scheme"]:
        result = test_endpoint("/query", {"question": query})
        print_result(query, result)
        
        # Verify intent
        if result.get("intent") == "scheme":
            print(f"{Colors.OKGREEN}✓ Intent correctly detected{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠ Intent mismatch: expected 'scheme', got '{result.get('intent')}'{Colors.ENDC}")
    
    # 5. Test Hybrid Intent Queries
    print(f"\n{Colors.BOLD}{Colors.WARNING}5. Testing HYBRID Intent Queries{Colors.ENDC}")
    for query in TEST_QUERIES["hybrid"]:
        result = test_endpoint("/query", {"question": query})
        print_result(query, result)
        
        # Verify intent
        if result.get("intent") == "hybrid":
            print(f"{Colors.OKGREEN}✓ Intent correctly detected{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠ Intent mismatch: expected 'hybrid', got '{result.get('intent')}'{Colors.ENDC}")
    
    # 6. Test Intent Detection Only
    print(f"\n{Colors.BOLD}6. Testing Intent Detection Endpoint{Colors.ENDC}")
    test_query = "What are the symptoms of citrus greening?"
    intent_result = test_endpoint("/test-intent", {"question": test_query})
    print(f"  Query: {test_query}")
    print(f"  Detected Intent: {intent_result.get('detected_intent', 'N/A')}")
    
    print(f"\n{Colors.BOLD}{Colors.OKGREEN}✓ Test Suite Completed!{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Error running tests: {str(e)}{Colors.ENDC}")
