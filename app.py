# app.py - The Streamlit Frontend for EchoMind

import streamlit as st
import requests
import pandas as pd

# --- Configuration ---
# This should be the address of your running FastAPI backend.
API_BASE_URL = "http://127.0.0.1:8000"
USER_ID = "default_user" # For this demo, we'll use a single, hardcoded user.

# --- Helper Functions to Talk to the API ---

def get_all_memories():
    """Fetches all memories for the user from the backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/memories/{USER_ID}")
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching memories: {e}")
        return []

def add_memory(content: str):
    """Sends a new memory to the backend."""
    if not content:
        st.warning("Memory content cannot be empty.")
        return
    try:
        payload = {"user_id": USER_ID, "content": content}
        response = requests.post(f"{API_BASE_URL}/add_memory", json=payload)
        response.raise_for_status()
        st.success("Memory added successfully!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error adding memory: {e}")

def delete_memory(memory_id: str):
    """Asks the backend to delete a memory by its ID."""
    try:
        response = requests.delete(f"{API_BASE_URL}/memory/{memory_id}")
        response.raise_for_status()
        st.toast(f"Memory forgotten!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting memory: {e}")

def post_chat_message(message: str):
    """Posts a chat message and gets the AI's response."""
    if not message:
        return None, None
    try:
        payload = {"user_id": USER_ID, "message": message}
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response"), data.get("memory_context")
    except requests.exceptions.RequestException as e:
        st.error(f"Error in chat: {e}")
        return "Sorry, I couldn't connect to the chat engine.", ""


# --- Streamlit App Layout ---

st.set_page_config(page_title="EchoMind", layout="wide")

st.title("🧠 EchoMind: Long-Term Memory Agent")
st.markdown("A prototype system that gives conversational AI a persistent, searchable memory.")

# --- Main App Columns ---
col1, col2 = st.columns([1.5, 1]) # Make the chat column wider

# --- Column 1: Chat Interface ---
with col1:
    st.header("💬 Chat with Memory")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "context" in message and message["context"]:
                 with st.expander("Memory Context Used"):
                    st.info(message["context"])

    # Accept user input
    if prompt := st.chat_input("What would you like to say?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.spinner("Thinking..."):
            assistant_response, memory_context = post_chat_message(prompt)
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
                if memory_context:
                    with st.expander("Memory Context Used"):
                        st.info(memory_context)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response, "context": memory_context}
        )


# --- Column 2: Memory Dashboard ---
with col2:
    st.header("📋 Memory Dashboard")

    # Manual Memory Addition
    with st.expander("Add a New Memory Manually"):
        with st.form("add_memory_form", clear_on_submit=True):
            new_memory_content = st.text_area("Enter a fact to remember:")
            submitted = st.form_submit_button("Save Memory")
            if submitted:
                add_memory(new_memory_content)

    # Display Memories
    st.subheader("Stored Memories")
    if st.button("🔄 Refresh Memories"):
        st.rerun()

    memories_data = get_all_memories()

    if memories_data:
        # Use pandas for better table formatting
        df = pd.DataFrame(memories_data)
        df = df[['content', 'is_active', 'id']] # Reorder columns
        df.rename(columns={'content': 'Memory Content', 'is_active': 'Active'}, inplace=True)
        
        # Create a new column with a "Forget" button for each memory
        df['Forget'] = [f"btn_{i}" for i in range(len(df))]
        
        # Display the dataframe with buttons
        for index, row in df.iterrows():
            col_mem, col_btn = st.columns([4, 1])
            with col_mem:
                status = "🟢 Active" if row['Active'] else "🔴 Inactive"
                st.info(f"{row['Memory Content']}\n*Status: {status}*")
            with col_btn:
                if st.button("Forget", key=row['Forget']):
                    delete_memory(row['id'])
                    st.rerun() # Refresh the page to show the change
            st.divider()

    else:
        st.write("No memories stored yet.")