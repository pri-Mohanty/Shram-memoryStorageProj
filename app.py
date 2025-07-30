from fastapi import FastAPI
from pydantic import BaseModel
from memory_store import MemoryStore
from retrieval_agent import RetrievalAgent

app = FastAPI()

store = MemoryStore("u1")
agent = RetrievalAgent(store)

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.post("/chat")
async def chat(req: ChatRequest):
    memory_context = ""
    print(f"🔍 Incoming message: {req.message}")
    if agent.should_trigger_memory(req.message):
        print("🧠 Memory retrieval triggered!")
        mems = agent.retrieve_context(req.message)
        print("🔍 Retrieved:", mems)
        memory_context = agent.format_for_prompt(mems)
    else:
        print("❌ Retrieval agent not triggered.")
    return {
        "memory_context": memory_context,
        "user_message": req.message
    }

class AddMemoryRequest(BaseModel):
    text: str
    category: str = None
    user_id: str

@app.post("/add_memory")
async def add_memory(req: AddMemoryRequest):
    store = MemoryStore(req.user_id)  # Ensures memory per user
    memory_id = store.add_memory(req.text, req.category)
    return {"message": "Memory added", "memory_id": memory_id}

from fastapi.responses import JSONResponse

@app.get("/get_memories/{user_id}")
async def get_memories(user_id: str):
    store = MemoryStore(user_id)
    raw = store.list_memories()
    result = [
        {
            "id": row[0],
            "text": row[2],
            "category": row[3],
            "timestamp": row[4]
        }
        for row in raw
    ]
    return JSONResponse(content=result)

@app.delete("/delete_memory/{memory_id}")
async def delete_memory(memory_id: str):
    store = MemoryStore("u1")  # for now, fixed to one user
    store.delete_memory(memory_id)
    return {"message": "Memory deleted"}
