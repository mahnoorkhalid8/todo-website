#!/usr/bin/env python3
"""
Test script to verify the chat parsing functionality for the new commands
"""

import re
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import the chat parsing logic
from routes.chat import parse_command_from_message

def parse_command(content, message_content):
    """Wrapper to match the function name used in the test"""
    return parse_command_from_message(message_content)

def test_chat_parsing():
    """Test the new chat parsing patterns"""

    test_cases = [
        # Test update description by name with "to"
        {
            "input": "update description of task cooking to biryani for dinner",
            "expected_action": "update_task",
            "expected_params": {
                "task_identifier": "cooking",
                "new_description": "biryani for dinner",
                "new_title": None,
                "new_due_date": None
            }
        },
        # Test update description by name with quotes
        {
            "input": "update description of task cooking \"biryani for dinner\"",
            "expected_action": "update_task",
            "expected_params": {
                "task_identifier": "cooking",
                "new_description": "biryani for dinner",
                "new_title": None,
                "new_due_date": None
            }
        },
        # Test toggle task to specific state
        {
            "input": "toggle task cooking to complete",
            "expected_action": "toggle_task",
            "expected_params": {
                "task_identifier": "cooking",
                "target_completed_state": True
            }
        },
        # Test simple toggle task
        {
            "input": "toggle task cooking",
            "expected_action": "toggle_task",
            "expected_params": {
                "task_identifier": "cooking",
                "target_completed_state": None
            }
        },
        # Test existing functionality to ensure it still works
        {
            "input": "update task description of task 1 Biryani for dinner",
            "expected_action": "update_task",
            "expected_params": {
                "task_identifier": "1",
                "new_description": "Biryani for dinner",
                "new_title": None,
                "new_due_date": None
            }
        },
        {
            "input": "add task cooking",
            "expected_action": "add_task",
            "expected_params": {
                "title": "cooking",
                "description": None,
                "due_date": None
            }
        }
    ]

    print("Testing chat parsing functionality...")
    print("="*60)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['input']}")

        # Parse the command
        result = parse_command(test_case['input'], test_case['input'])

        print(f"  Expected action: {test_case['expected_action']}")
        print(f"  Actual action:   {result['action']}")

        if result['action'] == test_case['expected_action']:
            print("  [PASS] Action matches")

            # Check params
            expected_params = test_case['expected_params']
            actual_params = result['params']

            param_match = True
            for key, expected_value in expected_params.items():
                if key in actual_params:
                    actual_value = actual_params[key]
                    if actual_value == expected_value:
                        print(f"    [OK] {key}: {actual_value}")
                    else:
                        print(f"    [FAIL] {key}: expected {expected_value}, got {actual_value}")
                        param_match = False
                else:
                    print(f"    [FAIL] {key}: missing from actual params")
                    param_match = False

            if param_match:
                print(f"  [PASS] Test {i} PASSED")
            else:
                print(f"  [FAIL] Test {i} FAILED - Parameter mismatch")
        else:
            print(f"  [FAIL] Test {i} FAILED - Action mismatch")

        print("-" * 40)

if __name__ == "__main__":
    test_chat_parsing()