import sys
import os
# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app from main module
try:
    # First try direct import (for when run from this directory)
    from main import create_app
    app = create_app()
except ImportError:
    try:
        # Alternative import method
        import main
        app = main.create_app()
    except ImportError as e:
        print(f"Import error: {e}")
        # Create a minimal app for error handling
        from fastapi import FastAPI
        app = FastAPI()

        @app.get("/")
        def read_root():
            return {"error": "Application failed to start properly", "details": str(e)}

# This is the entry point for Hugging Face Spaces
# Note: Hugging Face Spaces is primarily for ML applications
# For a full-stack web app like this, other platforms like Vercel, Render, or Railway are more appropriate

# The FastAPI app is available as the main interface
# Access the API documentation at /docs when deployed

# For Hugging Face Space compatibility
def main():
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()