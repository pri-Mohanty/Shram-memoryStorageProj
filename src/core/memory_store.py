import chromadb
import sqlite3
import uuid
from datetime import datetime
from src.config import CHROMA_PERSIST_DIRECTORY, CHROMA_COLLECTION_NAME, SQLITE_DB_PATH
from src.core.embedder import Embedder

class MemoryStore:
    """
    Handles the storage, retrieval, and soft deletion of memories.
    Uses ChromaDB for vector storage and SQLite for metadata.
    """
    def __init__(self):
        self.embedder = Embedder()
        
        # Initialize ChromaDB client and collection
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIRECTORY)
        self.collection = self.chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

        # Initialize SQLite connection and create table if it doesn't exist
        self.sqlite_conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
        self.sqlite_conn.isolation_level = None # Enable autocommit mode
        self._create_metadata_table()

    def _create_metadata_table(self):
        """Creates the SQLite table for memory metadata if it doesn't exist."""
        with self.sqlite_conn:
            self.sqlite_conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1
                );
            """)

    def add_memory(self, user_id: str, content: str):
        """
        Adds a new memory to both ChromaDB and SQLite.

        Args:
            user_id: The identifier for the user.
            content: The text content of the memory.
        
        Returns:
            The unique ID of the newly created memory.
        """
        memory_id = str(uuid.uuid4())
        embedding = self.embedder.get_embedding(content, task_type="RETRIEVAL_DOCUMENT")
        
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            metadatas=[{"user_id": user_id, "content": content}]
        )
        
        with self.sqlite_conn:
            self.sqlite_conn.execute(
                "INSERT INTO memories (id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
                (memory_id, user_id, content, datetime.utcnow())
            )
        print(f"✅ Added memory [{memory_id}]: '{content}'")
        return memory_id

# Replace the existing function with this new, heavily logged version.

    def retrieve_relevant_memories(self, user_id: str, query_text: str, k: int):
        """
        Retrieves the top-k most relevant active memories for a given query.
        This version includes extra logging for deep debugging.
        """
        query_embedding = self.embedder.get_embedding(query_text, task_type="RETRIEVAL_DOCUMENT")
        
        # Get the list of IDs for memories that are currently active from SQLite.
        active_memory_ids = self._get_active_memory_ids(user_id)
        
        # --- NEW DIAGNOSTIC LOGGING ---
        print("\n--- Preparing to Query Vector Store ---")
        print(f"User: '{user_id}'")
        print(f"Active Memory IDs found in SQLite: {active_memory_ids}")
        # --- END DIAGNOSTIC LOGGING ---
        
        if not active_memory_ids:
            print("No active IDs found, returning empty result.")
            print("-------------------------------------\n")
            return [], []

        # Query ChromaDB using the correct filters.
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, len(active_memory_ids)),
            where={"user_id": user_id},
            ids=active_memory_ids
        )
        
        # --- NEW DIAGNOSTIC LOGGING ---
        retrieved_ids = results.get('ids', [[]])[0]
        print(f"ChromaDB query returned {len(retrieved_ids)} results.")
        print(f"Retrieved IDs from ChromaDB: {retrieved_ids}")
        print("-------------------------------------\n")
        # --- END DIAGNOSTIC LOGGING ---

        return results.get('metadatas', [[]])[0], results.get('distances', [[]])[0]
        
    def _get_active_memory_ids(self, user_id: str) -> list[str]:
        """Helper to get all active memory IDs for a user from SQLite."""
        with self.sqlite_conn:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT id FROM memories WHERE user_id = ? AND is_active = 1", (user_id,))
            return [row[0] for row in cursor.fetchall()]

    def soft_delete_memory(self, memory_id: str):
        """Marks a memory as inactive in SQLite. This prevents it from being retrieved."""
        with self.sqlite_conn:
            self.sqlite_conn.execute("UPDATE memories SET is_active = 0 WHERE id = ?", (memory_id,))
        print(f"🗑️ Soft-deleted memory {memory_id}")

    def get_all_memories(self, user_id: str):
        """Returns all memories (active and inactive) for a user from SQLite."""
        with self.sqlite_conn:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT id, content, created_at, is_active FROM memories WHERE user_id = ?", (user_id,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]