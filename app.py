import streamlit as st
import os
import logging
import nav
# from home_page import home_page

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enable query logging if DEBUG_QUERIES environment variable is set
# if os.getenv("DEBUG_QUERIES", "").lower() in ("true", "1", "yes"):
logging.getLogger('database.db_manager').setLevel(logging.DEBUG)
logger.info("Query logging enabled (DEBUG level)")

# Page configuration
st.set_page_config(
    page_title="AI + Backend Developer Portfolio - Bryce Rodgers",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def home_page():
    """Home page content"""
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
    st.title("Welcome to Bryce Rodgers AI Portfolio 🤖")

    st.markdown("""
    <p style="font-size: 16px;">
    I am a Senior Software Engineer and Applied Machine Learning Engineer specializing in full-stack AI systems, serverless architecture, and modern cloud infrastructure. 
    This portfolio highlights deployed ML applications spanning computer vision, large language models, retrieval-augmented generation, and document intelligence workflows.
    Each project demonstrates end-to-end implementation—from model training and data pipelines to cloud-hosted inference services and scalable backend architecture.
    You can view the source code for this application <a href="https://github.com/BryceRodgers7/resume-app">here</a>.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🎯 What You'll Find Here
        
        - **Customer Support Chatbot**: An agentic customer support system with intelligent routing
        - **Image Classifier**: A custom-trained image classification model
        - **Simple Chatbot**: Interactive chatbot with a customizable system prompt
        - **Text-to-Image Generator**: Create images from text using Stability AI
        - **Custom GPT Model**: A 11-million parameter GPT model I trained from scratch
        - **Architecture**: A serverless architecture diagram for this application
        - **About Me**: A page about me and my background
        
        """)

    with col2:
        st.markdown("### 🔧 Technologies Used")
        tech_col1, tech_col2 = st.columns(2)
        
        with tech_col1:
            st.markdown("""
            - Python 
            - Streamlit
            - Docker
            - PostgreSQL
            - Qdrant
            - Google Cloud Run
            """)
        
        with tech_col2:
            st.markdown("""
            - PyTorch
            - Transformers
            - Stability AI API
            - OpenAI API
            - Fly.io
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



# import navigation
nav.config_navigation(home_page)