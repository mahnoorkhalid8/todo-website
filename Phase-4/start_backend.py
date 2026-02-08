import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)