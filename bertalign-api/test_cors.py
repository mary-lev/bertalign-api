#!/usr/bin/env python3
"""
Quick test script to verify CORS headers are properly configured.
"""

import requests
import sys

def test_cors_headers(base_url="http://localhost:8000"):
    """Test that CORS headers are present in API responses."""
    
    print(f"Testing CORS configuration at {base_url}")
    
    try:
        # Test preflight request (OPTIONS)
        print("\n1. Testing preflight OPTIONS request...")
        options_response = requests.options(
            f"{base_url}/align",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        print(f"   Status: {options_response.status_code}")
        print(f"   CORS headers present:")
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Credentials"
        ]
        
        for header in cors_headers:
            value = options_response.headers.get(header, "NOT PRESENT")
            print(f"     {header}: {value}")
        
        # Test actual POST request
        print("\n2. Testing actual POST request with CORS headers...")
        post_response = requests.post(
            f"{base_url}/align",
            headers={
                "Origin": "http://localhost:3000",
                "Content-Type": "application/json"
            },
            json={
                "source_text": "Hello world.",
                "target_text": "Bonjour le monde.",
                "source_language": "en",
                "target_language": "fr"
            }
        )
        
        print(f"   Status: {post_response.status_code}")
        cors_origin = post_response.headers.get("Access-Control-Allow-Origin", "NOT PRESENT")
        print(f"   Access-Control-Allow-Origin: {cors_origin}")
        
        # Test health endpoint
        print("\n3. Testing health endpoint...")
        health_response = requests.get(
            f"{base_url}/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        print(f"   Status: {health_response.status_code}")
        cors_origin = health_response.headers.get("Access-Control-Allow-Origin", "NOT PRESENT")
        print(f"   Access-Control-Allow-Origin: {cors_origin}")
        
        print("\n✅ CORS configuration test completed!")
        
        # Summary
        if options_response.status_code == 200 and cors_origin == "*":
            print("✅ CORS is properly configured for frontend requests")
            return True
        else:
            print("❌ CORS configuration may have issues")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}. Make sure the API server is running.")
        print("   Start the server with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error testing CORS: {e}")
        return False

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = test_cors_headers(base_url)
    sys.exit(0 if success else 1)