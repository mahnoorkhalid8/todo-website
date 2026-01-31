#!/usr/bin/env python3
"""
Manual Task Creation Guide
==========================

This script demonstrates the correct way to manually create tasks via API calls.
The "unprocessable content" error typically occurs due to missing required fields
or incorrect request formatting.
"""

import json
import requests

def create_task_example():
    """
    Example of how to correctly create a task manually
    """
    print("=== Manual Task Creation Guide ===\n")

    print("1. Register a user first (if needed):")
    print("curl -X POST 'http://127.0.0.1:8000/api/auth/register' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"email\":\"your-email@example.com\",\"password\":\"Password123!\",\"name\":\"Your Name\"}'\n")

    print("2. Login to get your authentication token:")
    print("curl -X POST 'http://127.0.0.1:8000/api/auth/login' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"email\":\"your-email@example.com\",\"password\":\"Password123!\"}'\n")

    print("3. Create a task with the obtained token (replace YOUR_TOKEN with actual token):")
    print("curl -X POST 'http://127.0.0.1:8000/api/tasks/' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -H 'Authorization: Bearer YOUR_TOKEN' \\")
    print("  -d '{\"title\":\"Your Task Title\",\"description\":\"Optional description\"}'\n")

    print("=== Common Causes of 'Unprocessable Content' Error ===\n")

    print("1. Missing required fields:")
    print("   [X] Missing 'title' field - 'title' is required")
    print("   [OK] Correct: {\"title\":\"Task Title\"}")
    print("   [OK] With description: {\"title\":\"Task Title\",\"description\":\"Task Description\"}\n")

    print("2. Invalid JSON format:")
    print("   [X] Missing quotes around field names: {title:\"Task Title\"}")
    print("   [OK] Correct: {\"title\":\"Task Title\"}\n")

    print("3. Missing authentication:")
    print("   [X] No Authorization header")
    print("   [OK] Correct: -H 'Authorization: Bearer YOUR_TOKEN'\n")

    print("4. Incorrect content type:")
    print("   [X] Wrong: Content-Type: text/plain")
    print("   [OK] Correct: -H 'Content-Type: application/json'\n")

    print("=== Valid Task Payload Examples ===\n")

    examples = [
        {
            "title": "Simple task with just title",
        },
        {
            "title": "Task with description",
            "description": "This is a detailed description of the task"
        },
        {
            "title": "Task with due date",
            "description": "This task has a deadline",
            "due_date": "2026-12-31T23:59:59"
        }
    ]

    for i, example in enumerate(examples, 1):
        print(f"{i}. {json.dumps(example)}")

def check_api_health():
    """
    Check if the API is accessible
    """
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code == 200:
            print("\n[OK] API is accessible and healthy")
        else:
            print(f"\n[WARN] API returned status code: {response.status_code}")
    except Exception as e:
        print(f"\n[ERROR] API is not accessible: {str(e)}")

if __name__ == "__main__":
    create_task_example()
    check_api_health()
    print("\n=== Troubleshooting Steps ===")
    print("1. Ensure the backend server is running on http://127.0.0.1:8000")
    print("2. Register/login to obtain a valid authentication token")
    print("3. Always include the Authorization header with your token")
    print("4. Ensure the title field is present in your request")
    print("5. Verify JSON formatting is correct")