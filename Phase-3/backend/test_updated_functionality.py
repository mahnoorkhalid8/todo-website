#!/usr/bin/env python3
"""
Test the updated functionality including the new due date parsing
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_updated_parsing():
    """Test the new chat parsing patterns"""

    try:
        from routes.chat import parse_command_from_message

        test_cases = [
            # Test the new due date update format
            {
                "input": "update due date of task aa to 04-02-2026",
                "expected_action": "update_task",
                "description": "Update due date with 'to' format"
            },
            {
                "input": "update due date of task aa to \"04-02-2026\"",
                "expected_action": "update_task",
                "description": "Update due date with quotes"
            },
            # Test existing functionality still works
            {
                "input": "update description of task cooking to biryani for dinner",
                "expected_action": "update_task",
                "description": "Update description (should still work)"
            },
            {
                "input": "toggle task cooking to complete",
                "expected_action": "toggle_task",
                "description": "Toggle task (should still work)"
            },
            {
                "input": "add task buy groceries",
                "expected_action": "add_task",
                "description": "Add task (should still work)"
            }
        ]

        print("Testing Updated AI Assistant Chat Command Parsing")
        print("="*70)

        passed = 0
        total = len(test_cases)

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['description']}")
            print(f"Input: '{test_case['input']}'")

            try:
                # Parse the command
                result = parse_command_from_message(test_case['input'])

                actual_action = result['action']
                expected_action = test_case['expected_action']

                print(f"Expected: {expected_action}")
                print(f"Actual:   {actual_action}")

                if actual_action == expected_action:
                    print("[PASS]")
                    if 'params' in result:
                        print(f"  Params: {result['params']}")
                    passed += 1
                else:
                    print("[FAIL]")

            except Exception as e:
                print(f"[ERROR]: {str(e)}")

        print("\n" + "="*70)
        print(f"SUMMARY: {passed}/{total} tests passed")

        if passed == total:
            print("[SUCCESS] ALL TESTS PASSED! The updated command parsing is working.")
        else:
            print(f"[WARNING] {total - passed} tests failed.")

        print("="*70)

    except ImportError as e:
        print(f"Could not import chat module: {e}")

if __name__ == "__main__":
    test_updated_parsing()