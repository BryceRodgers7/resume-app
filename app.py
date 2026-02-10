import streamlit as st
import os
import logging

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
    st.title("Welcome to My AI Portfolio 🤖")

    st.markdown("""
    ## About Me

    Welcome! I'm a senior software engineer with a passion for AI/ML, serverless architectures, backend systems, 
    trading, an MBA and a US Patent to top it all off. 
    This portfolio showcases several AI/ML projects I've developed that demonstrate full-stack capabilities, 
    from user-facing applications and backend services to cloud deployment, data architecture, and machine learning systems.
    ---
    """)

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


# Configure navigation with custom labels
pages = {
    "": [
        st.Page(home_page, title="Home", icon="🏠", default=True),
        st.Page("pages/support_agent.py", title="Support Agent", icon="💬"),
        st.Page("pages/image_classifier.py", title="Image Classifier", icon="🖼️"),
        st.Page("pages/pirate_chatbot.py", title="Pirate Chatbot", icon="🏴‍☠️"),
        st.Page("pages/stability.py", title="Stability", icon="🎨"),
        st.Page("pages/voyager_gpt.py", title="Voyager GPT", icon="🚀"),
        st.Page("pages/architecture.py", title="Architecture", icon="🏗️"),
        st.Page("pages/about_me.py", title="About Me", icon="👤"),
    ],
}

pg = st.navigation(pages)
pg.run()
