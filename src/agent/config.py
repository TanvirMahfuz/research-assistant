import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]

# Config values loaded from environment with safe defaults
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Model choice; change if needed
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Agent defaults
DEFAULT_TOPIC = os.getenv("RESEARCH_TOPIC", "Agentic AI Workflows 2026")
SEARCH_MAX = int(os.getenv("SEARCH_MAX", "8"))
LATEX_FILE = ROOT / "research_log.tex"

# Network settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
GROQ_RETRY = int(os.getenv("GROQ_RETRY", "2"))
