from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

# Print environment variables to confirm they're loaded
print("Environment variables loaded")
print(f"BETTER_AUTH_SECRET available: {'Yes' if os.getenv('BETTER_AUTH_SECRET') else 'No'}")
print("Starting simple server to confirm JWT functionality...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)