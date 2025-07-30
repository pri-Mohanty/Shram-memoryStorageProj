import google.generativeai as genai
from src.config import GOOGLE_API_KEY, EMBEDDING_MODEL

class Embedder:
    """A wrapper for Google Gemini's embedding API."""
    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=GOOGLE_API_KEY)

    def get_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        """
        Generates an embedding for the given text using a Gemini model.

        Args:
            text: The text to embed.
            task_type: The task type for the embedding. Can be "RETRIEVAL_QUERY"
                       for user queries or "RETRIEVAL_DOCUMENT" for storing memories.

        Returns:
            A list of floats representing the vector embedding.
        """
        try:
            # Note: Gemini's embedding model returns a 768-dimensional vector.
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type=task_type
            )
            return result['embedding']
        except Exception as e:
            print(f"Error getting embedding for text: '{text}'. Error: {e}")
            return [0.0] * 768 # Return a zero vector on failure