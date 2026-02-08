import os
import sys

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
os.environ['SECRET_KEY'] = 'o2nmkwIUqotG5dDCWR0a0rk2Uk2rL0DPBvqbdkwZ54N'

def patch_main():
    # Import the original app
    from main import create_app

    # Get the app
    app = create_app()

    # Override the exception handler to provide more details
    @app.exception_handler(500)
    async def detailed_internal_error_handler(request, exc):
        import traceback
        error_details = {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc),
                "details": traceback.format_exc()
            }
        }
        print(f"Internal server error: {error_details}")  # Log to console
        return {
            "status_code": 500,
            "content": error_details
        }

    return app

if __name__ == "__main__":
    import uvicorn
    app = patch_main()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)