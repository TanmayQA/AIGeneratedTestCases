from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    AZURE_ORG = os.getenv("AZURE_ORG")
    AZURE_PROJECT = os.getenv("AZURE_PROJECT")
    AZURE_PAT = os.getenv("AZURE_PAT")
    AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "7.1")


    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "ollama").lower()

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
