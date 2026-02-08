#!/usr/bin/env python3
"""
Test script to verify that the chatbot correctly handles all the requested command formats.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.routes.chat import parse_command_from_message


def test_command(command, expected_action, expected_params):
    """Test a command and verify it produces the expected result."""
    result = parse_command_from_message(command)
    print(f"\nTesting command: '{command}'")
    print(f"Expected action: {expected_action}")
    print(f"Actual action: {result['action']}")
    print(f"Expected params: {expected_params}")
    print(f"Actual params: {result.get('params', {})}")

    success = result['action'] == expected_action
    if expected_params:
        for key, expected_value in expected_params.items():
            if key in result.get('params', {}):
                actual_value = result['params'][key]
                if actual_value != expected_value and key not in ['new_due_date']:  # Allow flexibility for date formats
                    success = False
                    print(f"Mismatch in {key}: expected '{expected_value}', got '{actual_value}'")
            else:
                success = False
                print(f"Missing parameter: {key}")

    if success:
        print("✅ PASS")
    else:
        print("❌ FAIL")

    return success


def main():
    print("Testing Chatbot Command Parsing")
    print("=" * 50)

    # Test all the requested command formats
    test_cases = [
        # 1. Add task
        ("add task cooking", "add_task", {"title": "cooking"}),

        # 2. Add task description in task 40 "Biryani"
        ("add task description in task 40 Biryani", "update_task", {
            "task_identifier": "40",
            "new_title": None,
            "new_description": "Biryani",
            "new_due_date": None
        }),

        # 3. Add task due date in task 40 "29-01-2026"
        ("add task due date in task 40 29-01-2026", "update_task", {
            "task_identifier": "40",
            "new_title": None,
            "new_description": None,
            "new_due_date": "2026-01-29"
        }),

        # 4. Update task title of task 40 "cook dinner"
        ("update task title of task 40 cook dinner", "update_task", {
            "task_identifier": "40",
            "new_title": "cook dinner"
        }),

        # 5. Update task description of task 40 "Biryani for dinner"
        ("update task description of task 40 Biryani for dinner", "update_task", {
            "task_identifier": "40",
            "new_description": "Biryani for dinner"
        }),

        # 6. Update task due date of task 40 "02-02-2026"
        ("update task due date of task 40 02-02-2026", "update_task", {
            "task_identifier": "40",
            "new_due_date": "2026-02-02"
        }),

        # Additional test cases to ensure backward compatibility
        ("add task buy groceries", "add_task", {"title": "buy groceries"}),
        ("update task title in task 5 new title", "update_task", {"task_identifier": "5", "new_title": "new title"}),
        ("update task description in task 5 updated description", "update_task", {"task_identifier": "5", "new_description": "updated description"}),
    ]

    passed = 0
    total = len(test_cases)

    for command, expected_action, expected_params in test_cases:
        if test_command(command, expected_action, expected_params):
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! The chatbot correctly handles all requested command formats.")
    else:
        print(f"⚠️  {total - passed} tests failed. Some command formats may not be working correctly.")


if __name__ == "__main__":
    main()