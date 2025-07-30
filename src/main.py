from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from src.core.memory_store import MemoryStore
from src.core.memory_engine import MemoryEngine

# Create the data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# --- App Initialization ---
app = FastAPI(
    title="EchoMind API",
    description="API for a long-term memory agent powered by Gemini.",
    version="1.0.0"
)

# --- Singleton Instances ---
memory_store = MemoryStore()
memory_engine = MemoryEngine(memory_store)

# --- API Models ---
class ChatRequest(BaseModel):
    user_id: str = "default_user"
    message: str

class ChatResponse(BaseModel):
    response: str
    memory_context: str | None

class AddMemoryRequest(BaseModel):
    user_id: str = "default_user"
    content: str

class MemoryResponse(BaseModel):
    id: str
    content: str
    created_at: str
    is_active: bool

# --- API Routes ---
@app.post("/chat", response_model=ChatResponse)
async def chat_with_memory(request: ChatRequest):
    """
    Main chat endpoint that uses memory to generate a response.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    response, context = memory_engine.process_chat(request.user_id, request.message)
    return ChatResponse(response=response, memory_context=context or "")

@app.post("/add_memory", status_code=201)
async def add_memory_manually(request: AddMemoryRequest):
    """
    Manually add a memory for a user.
    """
    if not request.content:
        raise HTTPException(status_code=400, detail="Memory content cannot be empty.")
        
    memory_id = memory_store.add_memory(request.user_id, request.content)
    return {"message": "Memory added successfully", "memory_id": memory_id}

@app.get("/memories/{user_id}", response_model=list[MemoryResponse])
async def get_user_memories(user_id: str):
    """
    Retrieve all memories (active and inactive) for a specific user.
    """
    memories = memory_store.get_all_memories(user_id)
    return memories

@app.delete("/memory/{memory_id}", status_code=200)
async def forget_memory(memory_id: str):
    """
    Soft-deletes a memory by its unique ID, marking it as inactive.
    """
    memory_store.soft_delete_memory(memory_id)
    return {"message": f"Memory {memory_id} has been marked as inactive."}