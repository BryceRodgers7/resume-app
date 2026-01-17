import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI + Backend Developer Portfolio - Bryce Rodgers",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🤖 AI Portfolio")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Links")
st.sidebar.markdown("[GitHub](https://github.com/BryceRodgers7)")
st.sidebar.markdown("[Business Website] Coming Soon!")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/bryce-rodgers-dat7/)")

# Main content
st.title("Welcome to My AI Portfolio 🤖")

st.markdown("""
## About Me

Welcome! I'm an AI/ML practitioner passionate about building intelligent systems. 
This portfolio showcases several projects I've developed over the past couple of years.

---
""")

# Create columns for better layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🎯 What You'll Find Here
    
    - **Customer Support Chatbot**: An agentic customer support system with intelligent routing
    - **Custom GPT Model**: A 11-million parameter GPT model I trained from scratch
    - **Text-to-Image Generator**: Create images from text using Stability AI
    - **Image Classifier**: A custom-trained image classification model
    - **Simple Chatbot**: Interactive chatbot with customizable system prompts
    """)

with col2:
    st.markdown("""
    ### 🔧 Technologies Used
    
    - Python & Streamlit
    - PyTorch & TensorFlow
    - Transformers
    - Stability AI API
    - OpenAI API
    - Custom ML Models
    """)

st.markdown("---")

st.markdown("""
### 🌐 Connect With Me

Feel free to explore the demos using the navigation on the left. You can also find me at:
""")

# Create buttons for links
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📁 View My GitHub", use_container_width=True):
        st.markdown("[GitHub Profile](https://github.com/BryceRodgers7)")

with col2:
    if st.button("💼 My Business", use_container_width=True):
        st.info("Coming Soon!")

with col3:
    if st.button("💻 LinkedIn", use_container_width=True):
        st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/bryce-rodgers-dat7/)")

st.markdown("---")

st.info("👈 Use the sidebar to navigate between different projects and demos!")
