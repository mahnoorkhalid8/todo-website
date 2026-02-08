#!/usr/bin/env python3
"""
Direct test of the fix by importing fresh modules
"""

import sys
import os
import importlib

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_fix_directly():
    """Test the fix by importing fresh modules"""
    print("Testing the fix by importing fresh modules...")

    # Force reload of modules to get the updated version
    if 'db' in sys.modules:
        del sys.modules['db']
    if 'config' in sys.modules:
        del sys.modules['config']

    # Now import the updated modules
    from db import get_engine

    print("Getting engine with updated db.py...")
    try:
        engine = get_engine()
        print(f"Engine created successfully!")
        print(f"Engine URL: {engine.url}")

        # Check if it's the Neon URL
        if "neon.tech" in str(engine.url):
            print("✅ SUCCESS: Engine is configured for Neon database!")

            # Test connection
            with engine.connect() as conn:
                print("✅ SUCCESS: Connected to Neon database!")

                # Run a simple query
                result = conn.execute("SELECT version();")
                version = result.fetchone()[0]
                print(f"PostgreSQL version: {version.split(',')[0][:50]}...")

            return True
        else:
            print(f"❌ FAILURE: Engine is still pointing to local DB: {engine.url}")
            return False

    except Exception as e:
        print(f"❌ FAILURE: Error creating/getting engine: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fix_directly()
    if success:
        print("\n🎉 The fix is working! Neon database connection is now properly configured.")
    else:
        print("\n💥 The fix is not working yet.")