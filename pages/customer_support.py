import streamlit as st

def show():
    st.title("💬 Agentic Customer Support Chatbot")
    
    st.markdown("""
    This is an intelligent customer support chatbot that uses agentic workflows to handle
    customer inquiries effectively.
    
    ---
    """)
    
    st.info("""
    **🔧 Ready to integrate your existing code!**
    
    Replace this placeholder with your agentic customer support chatbot code.
    
    Tips for integration:
    - Keep all your existing logic
    - Make sure to use `st.session_state` for conversation history
    - Update any deprecated Streamlit functions to the latest API
    - Ensure API keys are loaded from secrets or environment variables
    """)
    
    st.markdown("### Example Structure:")
    st.code("""
# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Your chatbot UI here
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("How can I help you?"):
    # Your chatbot logic here
    pass
    """, language="python")
    
    st.markdown("---")
    st.warning("**Note:** Once you paste your code here, remove the placeholder content above.")
