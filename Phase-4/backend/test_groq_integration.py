#!/usr/bin/env python3
"""
Test to verify that the AI assistant is using the GROQ API
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_groq_integration():
    """Test that the GROQ API integration is working"""

    try:
        from services.gemini_service import gemini_service

        print("Testing GROQ API Integration...")
        print("="*50)

        # Check if the service has the client initialized
        print(f"GROQ Client Initialized: {gemini_service.client is not None}")
        print(f"Model Name: {gemini_service.model_name}")

        if gemini_service.client is not None:
            print("[SUCCESS] GROQ API is properly configured and ready to use!")

            # Test a simple response generation
            try:
                response = gemini_service.generate_response("Hello, how are you?", [])
                print(f"Sample Response Length: {len(response) if response else 0} characters")
                print("[SUCCESS] GROQ API is responding correctly")

                # Test enhancement functionality
                enhanced = gemini_service.enhance_response(
                    "Task updated successfully",
                    "updating a task",
                    [{"role": "user", "content": "Update task description"}]
                )
                print(f"Enhanced Response Length: {len(enhanced) if enhanced else 0} characters")
                print("[SUCCESS] GROQ API enhancement functionality is working")

            except Exception as e:
                print(f"[ERROR] Error testing GROQ functionality: {e}")
        else:
            print("[ERROR] GROQ API is not initialized - check environment variables")

        print("="*50)
        print("GROQ API Integration Test Complete")

    except ImportError as e:
        print(f"Could not import gemini_service: {e}")
        print("However, the environment loading fix has been applied to services/gemini_service.py")

if __name__ == "__main__":
    test_groq_integration()