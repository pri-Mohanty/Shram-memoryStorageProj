def format_memories_for_prompt(memories: list[dict]) -> str:
    """
    Formats a list of retrieved memories into a string for LLM injection.
    
    Args:
        memories: A list of memory dictionaries.
        
    Returns:
        A formatted string, or an empty string if no memories are provided.
    """
    if not memories:
        return ""
    
    header = "You have the following long-term memories about the user. Use them to provide a more personalized and accurate response:\n"
    
    formatted_memories = [f"- {mem['content']}" for mem in memories]
    
    return header + "\n".join(formatted_memories)