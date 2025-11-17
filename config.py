"""
Configuration file for the Magi System.
Customise these settings to match your LLM provider setup.
"""

# LLM Provider Selection
# Options: "lm_studio" or "gemini"
LLM_PROVIDER = "lm_studio"  # Change to "gemini" to use Google Gemini

# LM Studio Configuration
LM_STUDIO_URL = "http://127.0.0.1:1234/v1"
LM_STUDIO_MODEL = "openai/gpt-oss-20b"  # Change this to your loaded model name in LM Studio
LM_STUDIO_API_KEY = "lm-studio-local"  # Set to None for local LM Studio without API key

# Google Gemini Configuration
GEMINI_MODEL = "gemini-2.5-flash"  # Options: gemini-2.5-pro, gemini-2.5-flash, gemini-pro

# Agent Configuration
AGENT_TEMPERATURE = 0.7  # Creativity level (0.0 = deterministic, 1.0 = very creative)
AGENT_MAX_TOKENS = None  # Max response length (None = no limit)
AGENT_VERBOSE = True  # Show agent thinking process

# Judge Configuration
JUDGE_TEMPERATURE = 0.3  # Lower temperature for more consistent evaluation
JUDGE_MAX_TOKENS = None

# Memory Configuration
MEMORY_DB_PATH = "sqlite:///magi_agent_history.db"
CLEAR_MEMORY_ON_START = True  # Set to True to start fresh each time

# Search Configuration
SEARCH_ENABLED = True
MAX_SEARCH_RESULTS = 5

# Session Configuration
AUTO_SAVE_RESULTS = True  # Save results to JSON files automatically
RESULTS_DIR = "results"  # Directory to save results (created if doesn't exist)

# Example queries for testing
EXAMPLE_QUERIES = [
    "Should we invest in artificial general intelligence research?",
    "What are the implications of quantum computing for cybersecurity?",
    "How should society balance economic growth with environmental protection?",
    "What are the ethical considerations for autonomous weapons?",
    "How can we ensure AI systems are fair and unbiased?",
]
