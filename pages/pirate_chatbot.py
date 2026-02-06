import streamlit as st
import os
from openai import OpenAI

# Page configuration
st.set_page_config(
    page_title="Pirate Chatbot",
    page_icon="🏴‍☠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏴‍☠️ Pirate Chatbot")
st.write("Chat with an AI assistant - customize the system prompt to change its behavior!")

# Get API key from environment variables
if OPENAI_API_KEY := os.getenv('OPENAI_API_KEY'):
    st.sidebar.success('OpenAI API key is good.', icon='✅')
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    st.sidebar.warning('OpenAI API key not found in environment variables.', icon='⚠️')
    client = None

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful assistant who speaks like a pirate. Always respond in pirate speak with phrases like 'Ahoy!', 'Arr!', and 'me hearty'."

# System prompt textbox in sidebar
st.sidebar.subheader("System Prompt")
system_prompt = st.sidebar.text_area(
    "Customize how the AI should behave:",
    value=st.session_state.system_prompt,
    height=150,
    help="This controls the AI's personality and behavior"
)

# Update system prompt in session state if changed
if system_prompt != st.session_state.system_prompt:
    st.session_state.system_prompt = system_prompt

# Display chat history
st.subheader("Chat")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    if not client:
        st.error("Please set the OPENAI_API_KEY environment variable to use the chatbot.")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Prepare messages for API call
                api_messages = [
                    {"role": "system", "content": st.session_state.system_prompt}
                ] + st.session_state.messages
                
                # Stream the response
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=api_messages,
                    stream=True,
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error calling OpenAI API: {str(e)}")

# Clear chat button
st.divider()
if st.button("Clear Chat History", use_container_width=False):
    st.session_state.messages = []
    st.rerun()

