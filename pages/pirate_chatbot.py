import streamlit as st
import os
from openai import OpenAI
import nav
from app import home_page

# Page configuration
st.set_page_config(
    page_title="Pirate Chatbot",
    page_icon="🏴‍☠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

nav.config_navigation(home_page)

st.title("🏴‍☠️ Pirate Chatbot")

# Prevent auto-scroll on page load
st.markdown("""
<script>
    window.addEventListener('load', function() {
        setTimeout(function() {
            window.scrollTo(0, 0);
        }, 100);
    });
</script>
""", unsafe_allow_html=True)

st.markdown("""
### Interactive AI Chat with a Customizable System Prompt

This demo showcases **OpenAI GPT-3.5-turbo** integration with a fully customizable system prompt. 
The chatbot demonstrates real-time streaming responses and dynamic personality control through prompt engineering (right now it thinks it's a pirate, but you can change that!)
""")

with st.expander("🎯 What This Demonstrates", expanded=False):
    st.markdown("""
    - **OpenAI API Integration**: Direct API calls with streaming responses for real-time user experience
    - **Prompt Engineering**: Modify the system prompt in the sidebar to instantly change the AI's personality and behavior
    - **State Management**: Persistent conversation history and settings using Streamlit's session state
    - **Error Handling**: Graceful degradation and user-friendly error messages
    - **UI/UX Design**: Clean chat interface with real-time streaming indicators
    """)

with st.expander("🔧 Try It Out", expanded=False):
    st.markdown("""
    1. **Chat with the AI**: Ask questions, have conversations, or just say hello!
    2. **Customize the System Prompt** (sidebar): Change how the AI behaves—make it a professional consultant, a sentient robot like C3PO, or keep it as a pirate!
    3. **See Real-Time Streaming**: Watch responses generate character-by-character
    4. **Clear and Restart**: Test different prompts and conversation flows

    By default, the AI speaks like a pirate 🏴‍☠️—but you control the personality entirely through the system prompt.
    """)



st.write("Ready to chat? Try asking about the ocean, buried treasure, or anything else!")

# Get API key from environment variables
if OPENAI_API_KEY := os.getenv('OPENAI_API_KEY'):
    st.sidebar.success('OpenAI API key is good.', icon='✅')
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    st.sidebar.warning('OpenAI API key not found in environment variables.', icon='⚠️')
    client = None

# Initialize session state for chat history and system prompt
if "pirate_system_prompt" not in st.session_state:
    st.session_state.pirate_system_prompt = "You are a helpful assistant who speaks like a pirate. Always respond in pirate speak with phrases like 'Ahoy!', 'Arr!', and 'me hearty'."

if "pirate_messages" not in st.session_state:
    st.session_state.pirate_messages = []
    # Add initial greeting message using the current system prompt
    if client:
        try:
            # Get initial greeting from the AI using the system prompt from session state
            initial_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": st.session_state.pirate_system_prompt},
                    {"role": "user", "content": "Greet me and introduce yourself in one or two sentences."}
                ],
                max_tokens=100
            )
            greeting = initial_response.choices[0].message.content
            st.session_state.pirate_messages.append({"role": "assistant", "content": greeting})
        except Exception:
            # Fallback greeting if API call fails
            st.session_state.pirate_messages.append({
                "role": "assistant", 
                "content": "Hello! I'm your AI assistant. How can I help you today?"
            })

# System prompt textbox in sidebar
st.sidebar.subheader("System Prompt")
system_prompt = st.sidebar.text_area(
    "Customize how the AI should behave:",
    value=st.session_state.pirate_system_prompt,
    height=250,
    help="This controls the AI's personality and behavior"
)

# Update system prompt in session state if changed
if system_prompt != st.session_state.pirate_system_prompt:
    st.session_state.pirate_system_prompt = system_prompt

# Display chat history
st.subheader("Chat")
for message in st.session_state.pirate_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    if not client:
        st.error("Please set the OPENAI_API_KEY environment variable to use the chatbot.")
    else:
        # Add user message to chat history
        st.session_state.pirate_messages.append({"role": "user", "content": prompt})
        
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
                    {"role": "system", "content": st.session_state.pirate_system_prompt}
                ] + st.session_state.pirate_messages
                
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
                st.session_state.pirate_messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error calling OpenAI API: {str(e)}")

# Clear chat button
st.divider()
if st.button("Clear Chat History", use_container_width=False):
    st.session_state.pirate_messages = []
    st.rerun()

