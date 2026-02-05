"""
Application entry point for Hugging Face Spaces deployment.
"""
import os
import uvicorn
from src.main import app

# Get port from environment, default to 7860 for Hugging Face Spaces
port = int(os.environ.get("PORT", 7860))

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )