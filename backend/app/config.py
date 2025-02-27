import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    """Application configuration settings."""
    
    # Hugging Face API Key
    HUGGINGFACE_HUB_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")

    # OpenRouter API Key
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    # Upload Directory
    UPLOAD_DIR = "data/"

# Instantiate config
config = Config()