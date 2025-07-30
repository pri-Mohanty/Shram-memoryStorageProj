import sqlite3
import chromadb
import uuid
from datetime import datetime
from embedder import get_embedding
from chromadb.config import Settings
import os
from chromadb.config import Settings

class MemoryStore:
    def __init__(self, user_id: str):
        self.user_id = user_id
        CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma")
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=CHROMA_DIR,
            anonymized_telemetry=False
        ))

        self.collection = self.chroma_client.get_or_create_collection(name="memories")
        self.conn = sqlite3.connect("memory.sqlite")
        print("📦 Loaded collection with", self.collection.count(), "documents")
        self._setup_table()


    def _setup_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                text TEXT,
                category TEXT,
                timestamp TEXT,
                active INTEGER
            )
        ''')
        self.conn.commit()

    def add_memory(self, text: str, category: str = None) -> str:
        memory_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        embedding = get_embedding(text)

        self.collection.add(
            ids=[memory_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[{"user_id": self.user_id, "category": category}]
        )
        self.conn.execute('''
            INSERT INTO memories (id, user_id, text, category, timestamp, active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (memory_id, self.user_id, text, category, timestamp, 1))
        self.conn.commit()
        return memory_id

    def retrieve_memories(self, query: str, top_k: int = 3):
        embedding = get_embedding(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return results['documents'][0]

    def list_memories(self):
        cursor = self.conn.execute('SELECT * FROM memories WHERE active=1')
        return cursor.fetchall()

    def delete_memory(self, memory_id: str):
        self.conn.execute('UPDATE memories SET active=0 WHERE id=?', (memory_id,))
        self.conn.commit()
