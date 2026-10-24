
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import streamlit as st
from dotenv import load_dotenv, find_dotenv
import uuid

# Load the OpenAI API key from .env
load_dotenv(find_dotenv(), override=True)

# Configure the Streamlit page
st.set_page_config(
    page_title="Your Custom Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize the language model
chat = ChatOpenAI(
    model="gpt-5.2",
    temperature=0.5
)

# Initialize session state
if "chats" not in st.session_state:
    chat_id = str(uuid.uuid4())

    st.session_state.chats = {
        chat_id: {
            "title": "New Chat",
            "messages": [
                SystemMessage(
                    content="You are a helpful assistant."
                )
            ]
        }
    }

    st.session_state.current_chat = chat_id

if "current_chat" not in st.session_state:
    st.session_state.current_chat = next(
        iter(st.session_state.chats)
    )

# Get the current conversation
chat_id = st.session_state.current_chat
current_chat = st.session_state.chats[chat_id]
messages = current_chat["messages"]

# Sidebar
with st.sidebar:
    st.title("🤖 Your Custom ChatGPT")

    # Create a new conversation
    if st.button("＋ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())

        st.session_state.chats[new_id] = {
            "title": "New Chat",
            "messages": [
                SystemMessage(
                    content="You are a helpful assistant."
                )
            ]
        }

        st.session_state.current_chat = new_id
        st.rerun()

    st.divider()

    # Customize the system role for this conversation
    st.subheader("Assistant Settings")

    # Ensure the current conversation has a system message
    if not messages or not isinstance(messages[0], SystemMessage):
        messages.insert(
            0,
            SystemMessage(
                content="You are a helpful assistant."
            )
        )

    system_role = st.text_area(
        "System role",
        value=messages[0].content,
        key=f"system_role_{chat_id}",
        help="Define how your AI assistant should behave."
    )

    # Update the existing system message
    if system_role.strip():
        messages[0] = SystemMessage(content=system_role)

    st.divider()
    st.subheader("Chat History")

    # Show previous conversations
    for saved_id, saved_chat in reversed(
        list(st.session_state.chats.items())
    ):
        if st.button(
            saved_chat["title"],
            key=f"history_{saved_id}",
            use_container_width=True
        ):
            st.session_state.current_chat = saved_id
            st.rerun()

# Main chat interface
st.title("Your Custom ChatGPT 🤖")
st.caption("Ask a question and chat with your AI assistant.")

# Display previous messages
for msg in messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)

    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# User input
user_prompt = st.chat_input("Send a message...")

if user_prompt:
    # Save and display the user's message
    human_msg = HumanMessage(content=user_prompt)
    messages.append(human_msg)

    # Set the conversation title
    if current_chat["title"] == "New Chat":
        current_chat["title"] = user_prompt[:35]
        if len(user_prompt) > 35:
            current_chat["title"] += "..."

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate the AI response
    with st.chat_message("assistant"):
        with st.spinner("Working on your request..."):
            try:
                response = chat.invoke(messages)

                # Save and display the response
                ai_msg = AIMessage(content=response.content)
                messages.append(ai_msg)

                st.markdown(response.content)

            except Exception as error:
                # Remove the failed user message
                messages.pop()

                st.error(
                    f"Could not generate a response: {error}"
                )
