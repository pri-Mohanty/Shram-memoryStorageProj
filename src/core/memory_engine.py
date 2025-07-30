import google.generativeai as genai
import json
from src.core.memory_store import MemoryStore
from src.core.prompt_formatter import format_memories_for_prompt
from src.config import (
    GOOGLE_API_KEY, 
    CHAT_MODEL,
    MEMORY_RELEVANCE_THRESHOLD,
    TOP_K_MEMORIES
)

class MemoryEngine:
    """
    Orchestrates memory creation and retrieval using a single, optimized API call.
    """
    def __init__(self, memory_store: MemoryStore):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=GOOGLE_API_KEY)
        
        self.memory_store = memory_store
        # We only need one model now
        self.chat_model = genai.GenerativeModel(CHAT_MODEL)

# Replace the existing process_chat function with this one.

    def process_chat(self, user_id: str, message: str):
        """
        Main method to process a user's message, retrieve context,
        and get a response and a new memory in a single API call.
        """
        # 1. Retrieve and filter relevant memories
        retrieved_metadatas, retrieved_distances = self.memory_store.retrieve_relevant_memories(
            user_id=user_id, query_text=message, k=TOP_K_MEMORIES
        )
        
        # --- THIS IS THE LOGGING THAT WAS MISSING ---
        print("\n--- Memory Relevance Check ---")
        relevant_memories = []
        if retrieved_metadatas:
            for meta, dist in zip(retrieved_metadatas, retrieved_distances):
                similarity = 1 - dist
                print(f"Memory: '{meta['content']}' | Similarity: {similarity:.4f}")
                if similarity >= MEMORY_RELEVANCE_THRESHOLD:
                    relevant_memories.append(meta)
                    print("  ✅ -> Relevant enough, adding to context.")
                else:
                    print("  ❌ -> Not relevant enough, skipping.")
        else:
            print("No memories found for this user to check.")
        print("----------------------------\n")
        # --- END OF LOGGING BLOCK ---

        memory_context = format_memories_for_prompt(relevant_memories)

        # 2. Construct a single, powerful prompt for a JSON response
        system_instruction = f"""
You are a helpful and friendly assistant with a long-term memory.
Your task is to provide a conversational response to the user and to analyze the user's message to decide if a new memory should be saved.

{memory_context}

You MUST respond in a valid JSON format with two keys:
1. "response": A friendly, conversational response to the user's message. If context is provided, use it.
2. "memory_to_save": A single, concise fact about the user to be saved as a memory. If no new fact is present, this value MUST be null.

Example 1:
User message: "My favorite color is blue."
Your JSON response:
{{
  "response": "That's a great choice! I'll remember that your favorite color is blue.",
  "memory_to_save": "The user's favorite color is blue."
}}

Example 2:
User message: "What is my favorite color?"
Your JSON response:
{{
  "response": "Your favorite color is blue.",
  "memory_to_save": null
}}
"""
        # (The rest of the function remains the same)
        try:
            response = self.chat_model.generate_content(
                f"{system_instruction}\n\nUser message: \"{message}\"\nYour JSON response:"
            )
            
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            parsed_json = json.loads(cleaned_response)
            
            llm_response = parsed_json.get("response", "I'm sorry, I had trouble forming a response.")
            new_memory = parsed_json.get("memory_to_save")

            if new_memory:
                self.memory_store.add_memory(user_id, new_memory)

        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Error parsing LLM response: {e}\nRaw response: {response.text}")
            llm_response = "I'm sorry, I had a little hiccup. Could you try that again?"
            memory_context = ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            llm_response = f"Sorry, I encountered an error: {e}"
            memory_context = ""

        return llm_response, memory_context