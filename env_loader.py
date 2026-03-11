"""
env_loader.py
────────────────────
"""
import os
from dotenv import load_dotenv

def load_env():
    load_dotenv()
    return {
        "master_key": os.getenv("MASTER_KEY"),
        "github_token": os.getenv("GITHUB_TOKEN"),
        "deepseek_key": os.getenv("DEEPSEEK_API_KEY"),
        "gemini_key": os.getenv("GEMINI_API_KEY"),
        "cohere_key": os.getenv("COHERE_API_KEY"),
        "hf_token": os.getenv("HUGGINGFACE_TOKEN")
    }
