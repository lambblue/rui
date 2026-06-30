import secrets

def generate_key() -> str:
    """
    Generates a cryptographically random, secure session key.
    Uses secrets.token_hex(8) to generate a 16-character hexadecimal string.
    """
    return secrets.token_hex(8)

def rotate_keys(chat_history: list, old_key: str, new_key: str) -> list:
    """
    Updates the entire chat history by replacing the old session key with the new session key.
    This maintains the consistency of RUI wrapping tags and references across multi-turn histories
    while rotating keys to prevent delimiter leakage or replay attacks.

    Args:
        chat_history: List of message dictionaries, e.g., [{"role": "system", "content": "..."}]
        old_key: The session key used in the previous turn (can be None)
        new_key: The new session key for the current turn

    Returns:
        Updated list of message dictionaries with rotated keys.
    """
    if not old_key or old_key == new_key:
        return chat_history

    updated_history = []
    for msg in chat_history:
        new_msg = dict(msg)
        if "content" in new_msg and isinstance(new_msg["content"], str):
            new_msg["content"] = new_msg["content"].replace(old_key, new_key)
        updated_history.append(new_msg)
    
    return updated_history
