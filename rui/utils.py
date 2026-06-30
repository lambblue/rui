import json
from pathlib import Path

def format_chat_history(chat_history: list) -> str:
    """
    Pretty formats chat history for console printing.
    """
    formatted = []
    for msg in chat_history:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        formatted.append(f"[{role}]:\n{content}\n" + "-" * 40)
    return "\n".join(formatted)

def load_config() -> dict:
    """
    Loads API configurations from config.json.
    Searches first in the current working directory, then in the project root directory
    (the parent directory of the 'rui' package folder).
    
    Returns:
        dict: The loaded configuration with keys: api_provider, api_url, api_key, api_model.
              Defaults are returned if config.json is not found or parsing fails.
    """
    defaults = {
        "api_provider": "openai",
        "api_url": "https://api.openai.com/v1",
        "api_key": "",
        "api_model": "gpt-4o-mini",
        "api_reasoning_effort": "none"
    }
    
    # Try current working directory
    paths_to_try = [
        Path.cwd() / "config.json",
        Path(__file__).resolve().parent.parent / "config.json"
    ]
    
    for path in paths_to_try:
        if path.is_file():
            try:
                with path.open("r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**defaults, **config}
            except Exception as e:
                print(f"[RUI Warning] Failed to parse config at {path}: {e}")
                
    return defaults

