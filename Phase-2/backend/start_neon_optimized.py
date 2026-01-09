import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Print the database URL for debugging (without showing sensitive details)
    db_url = os.getenv('DATABASE_URL', '')
    print(f"Using database: {'Neon' if 'neon.tech' in db_url else 'Other'}")

    # Start the uvicorn server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )