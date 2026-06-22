import streamlit as st
from groq import Groq
import os

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)
# ============================================================
# GROQ CONFIG
# ============================================================

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# ==========================
# SESSION STATE
# ==========================
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ==========================
# HEADER
# ==========================
st.title("🤖 AI Chatbot")
st.caption("GPT Style Conversation Assistant")

# ==========================
# SIDEBAR
# ==========================
with st.sidebar:

    st.header("⚙️ Chat Controls")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()

    if st.button("❌ Delete Last Message"):
        if len(st.session_state.chat_messages) > 0:
            st.session_state.chat_messages.pop()
            st.rerun()

    st.markdown("---")

    st.subheader("📊 Chat Statistics")

    total_msgs = len(st.session_state.chat_messages)

    user_msgs = len([
        m for m in st.session_state.chat_messages
        if m["role"] == "user"
    ])

    ai_msgs = len([
        m for m in st.session_state.chat_messages
        if m["role"] == "assistant"
    ])

    st.write(f"Total Messages: {total_msgs}")
    st.write(f"User Messages: {user_msgs}")
    st.write(f"AI Messages: {ai_msgs}")

# ==========================
# CHAT DISPLAY
# ==========================
for msg in st.session_state.chat_messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================
# USER INPUT
# ==========================
prompt = st.chat_input("Ask me anything...")

# ==========================
# AI RESPONSE
# ==========================
if prompt:

    # Store User Message
    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:

        messages_for_ai = [
            {
                "role": "system",
                "content": """
You are an advanced AI assistant.

Rules:
- Remember previous conversation.
- Answer follow-up questions using chat history.
- Reply in Telugu if user asks in Telugu.
- Reply in English if user asks in English.
- Be professional and easy to understand.
- Give structured answers.
- Maintain context across the conversation.
"""
            }
        ]

        messages_for_ai.extend(
            st.session_state.chat_messages
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_for_ai,
            temperature=0.7,
            max_tokens=2048
        )

        answer = response.choices[0].message.content

    except Exception as e:

        answer = f"❌ Error: {str(e)}"

    # Save AI Response
    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)