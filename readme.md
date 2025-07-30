# 🧠 EchoMind: A Long-Term Memory Agent for LLMs (Gemini Edition)

EchoMind is a prototype system that gives conversational AI a persistent memory. It uses a sophisticated architecture to intelligently create, store, and retrieve memories across multiple conversations, powered by Google's Gemini models.

## Core Architecture

- **Backend API**: Built with **FastAPI**.
- **Memory Storage**:
  - **ChromaDB**: For storing and searching vector embeddings of memories.
  - **SQLite**: For storing structured metadata associated with each memory.
- **Intelligence**:
  - **Memory Engine**: A core module that decides what to remember and what to recall.
  - **Embeddings & Chat**: Uses **Google Gemini** models (`gemini-1.5-pro`, `text-embedding-004`).

## Getting Started

### 1. Prerequisites

- Python 3.9+
- A Google API Key from [Google AI Studio](https://aistudio.google.com/).

### 2. Setup

1.  **Clone the repository:**
    ```sh
    git clone <your_repo_url>
    cd echomind
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    - Rename `.env.example` to `.env`.
    - Add your Google API key to the `GOOGLE_API_KEY` variable in the `.env` file.

### 3. Running the Application

Launch the FastAPI server with Uvicorn:
```sh
uvicorn src.main:app --reload