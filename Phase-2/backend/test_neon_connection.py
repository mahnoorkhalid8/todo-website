#!/usr/bin/env python3
"""
Test script to check Neon database connection
"""

import sys
import os
import socket

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config import settings
import psycopg2
from urllib.parse import urlparse

def test_neon_connection():
    """Test Neon database connection"""
    print("Testing Neon database connection...")
    print(f"Database URL: {settings.DATABASE_URL}")

    # Parse the database URL
    parsed_url = urlparse(settings.DATABASE_URL)
    print(f"Hostname: {parsed_url.hostname}")
    print(f"Port: {parsed_url.port}")
    print(f"Database: {parsed_url.path[1:] if parsed_url.path else ''}")

    # Test DNS resolution
    print("\nTesting DNS resolution...")
    try:
        ip_address = socket.gethostbyname(parsed_url.hostname)
        print(f"DNS resolution successful: {parsed_url.hostname} -> {ip_address}")
    except socket.gaierror as e:
        print(f"DNS resolution failed: {e}")
        print("This indicates a network connectivity issue or an incorrect hostname.")
        return False

    # Test database connection
    print("\nTesting database connection...")
    try:
        conn = psycopg2.connect(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            database=parsed_url.path[1:],  # Remove leading '/'
            user=parsed_url.username,
            password=parsed_url.password
        )
        print("Database connection successful!")

        # Test with a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0][:50]}...")

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during connection: {e}")
        return False

if __name__ == "__main__":
    success = test_neon_connection()
    if success:
        print("\n✅ Neon database connection is working!")
    else:
        print("\n❌ Neon database connection is not working!")
        print("\nPossible solutions:")
        print("1. Check if your Neon project is active and not paused")
        print("2. Verify the connection string is correct")
        print("3. Check your internet connection and firewall settings")
        print("4. Make sure you have the necessary permissions")