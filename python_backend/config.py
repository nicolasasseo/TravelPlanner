"""
Configuration file for the Python backend.
Set these environment variables or modify the defaults as needed.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
NEXTJS_API_BASE = os.getenv("NEXTJS_API_BASE", "http://localhost:3000")
PYTHON_API_PORT = os.getenv("PYTHON_API_PORT", "8001")

# Database Configuration (if needed)
DATABASE_URL = os.getenv("DATABASE_URL", "")


# Validate required environment variables
def validate_config():
    """Validate that required environment variables are set"""
    missing_vars = []

    if not OPENAI_API_KEY:
        missing_vars.append("OPENAI_API_KEY")
    if not SERPAPI_API_KEY:
        missing_vars.append("SERPAPI_API_KEY")

    if missing_vars:
        print(f"⚠️  WARNING: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return False

    print("✅ Configuration validated successfully")
    return True


if __name__ == "__main__":
    validate_config()
