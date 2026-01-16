import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import app

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