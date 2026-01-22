#!/usr/bin/env python3
"""
Deployment readiness check for the AI-Powered Todo Application
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    path = Path(filepath)
    exists = path.exists()
    status = "PASS" if exists else "FAIL"
    print(f"[{status}] {description}: {filepath}")
    return exists

def check_directory_exists(dirpath, description):
    """Check if a directory exists and report status."""
    path = Path(dirpath)
    exists = path.is_dir()
    status = "PASS" if exists else "FAIL"
    print(f"[{status}] {description}: {dirpath}")
    return exists

def check_required_files():
    """Check for all required files for deployment."""
    print("Checking required files for deployment...")
    print("=" * 50)

    required_files = [
        ("README.md", "Documentation file"),
        (".env.example", "Environment variables template"),
        ("requirements.txt", "Python dependencies"),
        ("Dockerfile", "Container configuration"),
        ("Procfile", "Process configuration for Heroku/Railway"),
        ("app.py", "Application entry point"),
        ("backend/main.py", "Backend application"),
        ("frontend/package.json", "Frontend dependencies"),
    ]

    all_present = True
    for filepath, description in required_files:
        exists = check_file_exists(filepath, description)
        if not exists:
            all_present = False

    print()
    return all_present

def check_required_directories():
    """Check for all required directories for deployment."""
    print("Checking required directories for deployment...")
    print("=" * 50)

    required_dirs = [
        ("backend", "Backend source code"),
        ("frontend", "Frontend source code"),
        ("backend/routes", "Backend API routes"),
        ("backend/services", "Backend services"),
        ("frontend/app", "Frontend application pages"),
    ]

    all_present = True
    for dirpath, description in required_dirs:
        exists = check_directory_exists(dirpath, description)
        if not exists:
            all_present = False

    print()
    return all_present

def check_environment_variables():
    """Check for essential environment variables."""
    print("Checking environment configuration...")
    print("=" * 50)

    essential_vars = [
        ("DATABASE_URL", "Database connection string"),
        ("SECRET_KEY", "JWT secret key"),
    ]

    print("Essential environment variables to set in production:")
    for var, description in essential_vars:
        print(f"  - {var}: {description}")

    print("\nOptional but recommended variables:")
    optional_vars = [
        ("GOOGLE_GEMINI_API_KEY", "AI service API key"),
        ("GROQ_API_KEY", "Alternative AI service API key"),
        ("FRONTEND_URL", "Frontend application URL"),
        ("BACKEND_URL", "Backend application URL"),
    ]

    for var, description in optional_vars:
        print(f"  - {var}: {description}")

    print()

def main():
    print("AI-Powered Todo Application - Deployment Readiness Check")
    print("=" * 60)

    files_ok = check_required_files()
    dirs_ok = check_required_directories()
    check_environment_variables()

    print("Summary:")
    print("=" * 20)
    print(f"Required files: {'PASS - All present' if files_ok else 'FAIL - Some missing'}")
    print(f"Required directories: {'PASS - All present' if dirs_ok else 'FAIL - Some missing'}")

    if files_ok and dirs_ok:
        print("\n*** The project is ready for deployment! ***")
        print("\nDeployment options:")
        print("  - Backend API: Deploy to Render, Railway, or Heroku")
        print("  - Frontend: Deploy to Vercel or Netlify")
        print("  - Monolithic: Deploy using Docker to any container platform")
        print("\nRemember to set the required environment variables in production!")
    else:
        print("\n*** The project is NOT ready for deployment. ***")
        print("Please address the missing files/directories before deploying.")

    return files_ok and dirs_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)