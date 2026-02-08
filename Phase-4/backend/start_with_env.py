import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Print the database URL for debugging
    print(f"Using DATABASE_URL: {os.getenv('DATABASE_URL')}")

    # Start the uvicorn server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )