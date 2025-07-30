import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.set_page_config(layout="wide")

st.title("🧠 Long-Term Memory Agent Demo")

# Sidebar Navigation
section = st.sidebar.radio("Navigate", ["Add Memory", "Chat", "View/Delete Memory"])

if section == "Add Memory":
    st.subheader("➕ Add Memory")
    text = st.text_input("Memory text")
    category = st.text_input("Category (optional)")
    if st.button("Add"):
        r = requests.post(f"{BASE_URL}/add_memory", json={
            "text": text,
            "category": category,
            "user_id": "u1"
        })
        st.success(f"Memory added: {r.json()['memory_id']}")

elif section == "Chat":
    st.subheader("💬 Chat with Memory Agent")
    message = st.text_input("Your message")
    if st.button("Send"):
        r = requests.post(f"{BASE_URL}/chat", json={
            "message": message,
            "user_id": "u1"
        })

        res = r.json()
        st.markdown("### 🔍 Raw Response")
        st.json(res)  # ← shows entire response

elif section == "View/Delete Memory":
    st.subheader("📜 Current Memory Bank")
    r = requests.get(f"{BASE_URL}/get_memories/u1")
    for mem in r.json():
        with st.expander(f"{mem['text']}"):
            st.write(f"Category: {mem['category']}")
            st.write(f"Timestamp: {mem['timestamp']}")
            if st.button("🗑 Delete", key=mem["id"]):
                del_r = requests.delete(f"{BASE_URL}/delete_memory/{mem['id']}")
                st.success("Memory deleted — refresh to update.")
