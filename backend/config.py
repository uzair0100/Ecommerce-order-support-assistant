"""
Configuration settings for GadgetMart assistant backend.
"""

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"
MODEL_NAME = "qwen2.5:1.5b-instruct"

# Model parameters
TEMPERATURE = 0  # Deterministic responses
NUM_CTX = 4096   # Context window size

# Memory management
MAX_HISTORY_TURNS = 8  # Keep roughly last 8 turns (user + assistant pairs)
ESTIMATED_SYSTEM_TOKENS = 1200  # GadgetMart facts in system prompt
ESTIMATED_HISTORY_BUDGET = 2000  # Tokens for conversation history
ESTIMATED_GENERATION_BUDGET = 800  # Leave room for assistant response

# Session settings
SESSION_TIMEOUT_SECONDS = 3600  # 1 hour (not enforced yet, for future use)

# Store facts location
STORE_FACTS_FILE = "backend/gadgetmart_facts.txt"
