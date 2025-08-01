# 🧠 EchoMind: A Long-Term Memory Agent for LLMs

**EchoMind** is a fully functional prototype of a conversational AI system with persistent, long-term memory. This project demonstrates how to augment a Large Language Model (LLM)—in this case, Google's **Gemini**—with the ability to **intelligently store, recall, and forget** information across multiple conversations, leading to a more personalized and context-aware user experience.

The system is built with a **decoupled frontend and backend architecture**, showcasing a modern approach to building AI-powered applications.

---

## 🚀 Core Features

- **Intelligent Memory Creation**: Automatically extracts and saves new, meaningful facts from conversations.
- **Semantic Memory Retrieval**: Uses vector embeddings to find relevant memories based on meaning—not just keywords.
- **Dynamic Context Injection**: Supplies the AI with relevant memories so it can answer questions like _"What did I say my favorite tool was?"_
- **Memory Management UI**: Users can view, add, and “soft delete” memories via an intuitive dashboard.
- **Decoupled Architecture**:  
  - **FastAPI** backend for AI and memory logic  
  - **Streamlit** frontend for chat and memory control

---

## 🏛️ System Architecture

EchoMind is designed with a clear separation of concerns for scalability and maintainability.

### 1. Frontend – **Streamlit**
- Chat interface + memory management dashboard
- Communicates with the backend via HTTP requests

### 2. Backend – **FastAPI**
- Exposes endpoints for chat, memory creation, and management
- Orchestrates memory logic and Gemini API usage

### 3. Memory Engine – `MemoryEngine`
- Core logic engine
- Handles chat input, memory querying, and response generation using a single optimized Gemini API call

### 4. Memory Store – `MemoryStore`
Hybrid memory storage:
- **ChromaDB**: Vector DB for fast semantic search via embeddings
- **SQLite**: Stores metadata like creation date, active status, etc.

### 5. AI Models – **Google Gemini**
- `gemini-1.5-flash-latest`: Used for chat and memory extraction
- `models/text-embedding-004`: Powers semantic search via embeddings

---

## 🛠️ Getting Started

Follow these steps to get EchoMind running locally:

### 1. Prerequisites

- Python 3.9+
- Google API Key with Gemini access ([Google AI Studio](https://aistudio.google.com/))

### 2. Installation

#### Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
````

#### Create and Activate a Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Set Up Environment Variables

1. Rename `.env.example` → `.env`
2. Open `.env` and add your Gemini API key:

   ```env
   GEMINI_API_KEY="your_gemini_api_key_here"
   ```

---

## 🚦 Running the Application

Run the backend and frontend in **two separate terminal sessions**.

### Terminal 1 – Start the Backend

```bash
uvicorn src.main:app --reload
```

* Backend will run at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Terminal 2 – Start the Frontend

```bash
streamlit run app.py
```

* Frontend will launch at: [http://127.0.0.1:8501](http://127.0.0.1:8501)

---

## 📖 How to Use EchoMind

Once the app is running, interact via the Streamlit interface:

### ✅ Chat with the Agent

* Type messages in the chat input
* Try: *"My favorite animal is the wolf."*
  → This will be saved automatically as a memory

### 🔍 Recall a Memory

* Ask: *"What is my favorite animal?"*
  → The agent will use its memory and show the context it used

### 🧠 Manage Memories

Use the **Memory Dashboard** (right side panel):

* **Refresh Memories**: Load the latest list
* **Add Manually**: Insert a new memory directly
* **Forget**: Click “Forget” to soft-delete a memory (won’t be used in context anymore)

---

## 🎉 Congratulations!

You're now ready to explore a full-stack implementation of a long-term memory-augmented LLM. This project illustrates:

* The power of memory in LLMs
* Modern, decoupled architecture
* Real-time semantic search and response generation

```

Let me know if you'd like this saved as a downloadable file or embedded with badges/licenses.
```
