import sys
import os

# Add the current directory and parent directory to the path to handle different deployment scenarios
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the app from main module with multiple fallback strategies
def get_app():
    try:
        # First try direct import (for when run from this directory)
        from main import create_app
        return create_app()
    except ImportError as e:
        print(f"Initial import failed: {e}")
        try:
            # Alternative import method with explicit path
            import main
            return main.create_app()
        except ImportError as e2:
            print(f"Alternative import failed: {e2}")
            try:
                # Try importing with sys.path modifications
                sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
                import main
                return main.create_app()
            except ImportError as e3:
                print(f"Path modification import failed: {e3}")
                # Create a minimal app for error handling
                try:
                    from fastapi import FastAPI
                    app = FastAPI()

                    @app.get("/")
                    def read_root():
                        return {
                            "error": "Application failed to start properly",
                            "details": str(e3),
                            "fallback": "Basic app running but features may not be available"
                        }

                    return app
                except ImportError as e4:
                    # If even FastAPI can't be imported, we're in serious trouble
                    print(f"Critical import error: {e4}")
                    # Return a basic callable that can be used as an app
                    def minimal_app(environ, start_response):
                        status = '500 Internal Server Error'
                        headers = [('Content-type', 'application/json')]
                        start_response(status, headers)
                        return [b'{"error": "Application startup failed"}']

                    return minimal_app

app = get_app()

# This is the entry point for Hugging Face Spaces
# Note: Hugging Face Spaces is primarily for ML applications
# For a full-stack web app like this, other platforms like Vercel, Render, or Railway are more appropriate

# The FastAPI app is available as the main interface
# Access the API documentation at /docs when deployed

# For Hugging Face Space compatibility
def main():
    try:
        import uvicorn
        import os

        port = int(os.environ.get("PORT", 7860))
        uvicorn.run(app, host="0.0.0.0", port=port)
    except ImportError:
        print("Uvicorn not available, app started but not running server")

if __name__ == "__main__":
    main()