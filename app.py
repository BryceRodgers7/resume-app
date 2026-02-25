import streamlit as st
import os
import logging
import nav
from pathlib import Path
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

    photo_path = Path(__file__).parent.parent / '.static' / 'me.jpg'
    # display my photo (convert Path to string for Streamlit compatibility)
    st.image(str(photo_path), width=231, caption="Bryce Rodgers")

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
    st.sidebar.title("🤖 Portfolio")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔗 Links")
    st.sidebar.markdown("[GitHub](https://github.com/BryceRodgers7)")
    st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/bryce-rodgers-dat7/)")
    st.sidebar.markdown("[Givio](https://www.giviogives.com) A Discovery Platform for Non-Profit Donors (In Development)")

    # Main content
    st.title("Welcome to Bryce Rodgers AI Portfolio 🤖")

    st.markdown("""
    <p style="font-size: 16px;">
    I am a Senior Software Engineer and Applied Machine Learning Engineer with more than 15 years of experience building scalable backend systems, developer tooling, and data-driven applications. I specialize in full-stack AI systems, serverless architecture, and modern cloud infrastructure, with a focus on taking ideas from model training to production deployment.

    I’ve shipped large production systems at companies like Pearson and Samsung, designing reliable software used by millions of people. I hold a U.S. patent (US9299264B2 — Sound Assessment and Remediation) and have an academic foundation in Mathematics, Computer Science, and Business Administration. That background shapes how I approach engineering decisions — balancing technical rigor, practical outcomes, and long-term system design.

    In recent years, my work has centered on AI-driven applications and cloud-native ML workflows. This portfolio highlights deployed projects spanning computer vision, large language models, retrieval-augmented generation, and document intelligence systems. Each project demonstrates end-to-end implementation — from data pipelines and model training to cloud-hosted inference services and scalable backend architecture.

    I’m currently building a new application focused on connecting non-profit organizations with donors based on alignment of shared values. I’m particularly interested in practical AI systems that combine LLMs, vector search, and traditional software engineering to create reliable, usable tools.

    You can view the source code for this application <a href="https://github.com/BryceRodgers7/resume-app">here</a>.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
    ### 🚀 Deployed AI Systems

    - **Agentic Customer Support Platform**  
    Tool-enabled LLM system with semantic search, structured tool execution, and automated order workflows deployed via cloud-hosted APIs

    - **Custom Image Classification Pipeline**  
    Fine-tuned ResNet50 model with dataset curation, hard-negative mining, confidence calibration, and production inference endpoint

    - **Decoder-Only Transformer (11M Parameters)**  
    Custom-trained GPT-style language model with tokenization, training pipeline, and scalable cloud deployment

    - **LLM Document Intelligence Workflow**  
    End-to-end pipeline for extracting structured organizational data from unstructured grant proposals using LLMs and validation logic

    - **Text-to-Image Generation Service**  
    Stability AI integration with serverless backend and frontend orchestration
                    
    - **Interactive Prompt Engineering Sandbox**  
    Real-time streaming chatbot with dynamic system prompt control demonstrating OpenAI API integration and LLM behavior modulation

    - **System Architecture Overview**  
    Full-stack serverless infrastructure diagram covering frontend, API services, vector database, model hosting, and data storage
        
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




# import navigation
nav.config_navigation(home_page)