import streamlit as st

def show():
    st.title("🤖 Simple Chatbot with Custom System Prompt")
    
    st.markdown("""
    A simple chatbot where you can customize the system prompt to change its behavior.
    
    ---
    """)
    
    st.info("""
    **🔧 Ready to integrate your existing code!**
    
    Replace this placeholder with your simple chatbot code.
    
    Tips for integration:
    - Use `st.session_state` for conversation history
    - Store API keys securely in secrets
    - Use `st.chat_message` and `st.chat_input` for modern chat UI
    - Allow system prompt editing in a sidebar or expander
    """)
    
    st.markdown("### Example Structure:")
    st.code("""
import openai

# System prompt editor
with st.expander("🎛️ Edit System Prompt"):
    system_prompt = st.text_area(
        "System Prompt:",
        value="You are a helpful assistant.",
        height=100
    )

# Initialize chat history
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Display chat messages
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    
    # Get response from API
    with st.spinner("Thinking..."):
        response = get_chatbot_response(system_prompt, st.session_state.chat_messages)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    st.rerun()
    """, language="python")
    
    st.markdown("---")
    st.warning("**Note:** Once you paste your code here, remove the placeholder content above.")
