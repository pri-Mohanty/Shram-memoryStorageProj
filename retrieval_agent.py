import re
from typing import List
from memory_store import MemoryStore

RETRIEVE_PATTERNS = [
    r"what .* do i (use|like|have|prefer)",
    r"which .* did i mention",
    r"where do i (live|stay|work)",
    r"remind me.*",
    r"what .* did i say.*",
    r"do you remember.*"
]

class RetrievalAgent:
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    def should_trigger_memory(self, message: str) -> bool:
        msg = message.lower()
        return any(re.search(pattern, msg) for pattern in RETRIEVE_PATTERNS)

    def retrieve_context(self, message: str, top_k: int = 3) -> List[str]:
        return self.memory_store.retrieve_memories(message, top_k=top_k)

    def format_for_prompt(self, memories: List[str]) -> str:
        if not memories:
            return ""
        formatted = "\n".join([f"• {m}" for m in memories])
        return f"[MEMORY]\n{formatted}\n"
