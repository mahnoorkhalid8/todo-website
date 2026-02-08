#!/usr/bin/env python3
"""
Debug script to help troubleshoot manual task creation issues
"""

import subprocess
import json
import sys

def test_task_creation():
    print("=== Task Creation Debug Script ===\n")

    # Test 1: Check if servers are running
    print("1. Checking if servers are running...")
    try:
        result = subprocess.run(['curl', '-s', '-X', 'GET', 'http://127.0.0.1:8000/health'],
                              capture_output=True, text=True, timeout=10)
        if '"status":"healthy"' in result.stdout:
            print("   [OK] Backend server is running and healthy")
        else:
            print("   [ERROR] Backend server is not responding properly")
            return
    except:
        print("   [ERROR] Backend server is not accessible")
        return

    # Test 2: Show the exact error that occurs with missing title
    print("\n2. Demonstrating the 'Unprocessable Content' error:")
    print("   This error occurs when the required 'title' field is missing:")
    print('   Example: curl -X POST "http://127.0.0.1:8000/api/tasks/" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -H "Authorization: Bearer YOUR_VALID_TOKEN" \\')
    print('     -d "{}"')
    print("   Result: {'detail':[{'loc':['body','title'],'msg':'field required','type':'value_error.missing'}]}")

    # Test 3: Show correct format
    print("\n3. Correct format for task creation:")
    print("   curl -X POST 'http://127.0.0.1:8000/api/tasks/' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -H 'Authorization: Bearer YOUR_VALID_TOKEN' \\")
    print("     -d '{\"title\":\"Your Task Title\",\"description\":\"Optional description\"}'")

    # Test 4: Common mistakes
    print("\n4. Common mistakes that cause 'Unprocessable Content' error:")
    print("   [X] Missing title field: {\"description\":\"No title\"}")
    print("   [X] Invalid JSON: {title:\"Missing quotes\"}")
    print("   [X] Expired token: (need to log in again)")
    print("   [X] Empty request body")

    # Test 5: Steps to fix
    print("\n5. Steps to resolve the issue:")
    print("   [OK] Make sure the backend server is running on http://127.0.0.1:8000")
    print("   [OK] Register a user account if you don't have one")
    print("   [OK] Log in to get a valid authentication token")
    print("   [OK] Ensure your request includes the required 'title' field")
    print("   [OK] Use proper JSON formatting with double quotes")
    print("   [OK] Include both Content-Type and Authorization headers")
    print("   [OK] If you get 'Could not validate credentials', log in again for a new token")

    print("\n=== End of Debug Information ===")

if __name__ == "__main__":
    test_task_creation()