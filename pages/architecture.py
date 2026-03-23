import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import nav
from app import home_page

# Page configuration
st.set_page_config(
    page_title="Portfolio App Architecture",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

nav.config_navigation(home_page)

st.title("🏗️ Portfolio App Architecture")

st.markdown("""
The diagram below shows the complete **serverless/cloud-native** architecture of my Portfolio 
application, including deployment infrastructure, upstream delivery projectsapplication components, and external services.
            
See below the diagram for more details.

---
""")



deployment_col1, deployment_col2 = st.columns(2)

with deployment_col1:
    st.markdown("""
#### ☁️ Deployment Infrastructure
- **Fly.io**: Frontend hosting (Streamlit in Docker container)
- **Supabase**: Managed PostgreSQL database
- **Qdrant Cloud**: Vector database for semantic knowledge base
- **Google Cloud Run**: Serverless backend for custom inference APIs
- **OpenAI & Stability AI**: External API services
- **Upstream Projects**: Model training pipelines & Cloud Run Deployment
    
    """)

with deployment_col2:
    st.markdown("""
#### 🔑 Key Benefits of Serverless
- ✅ **Automatic Scaling**: All services scale based on demand
- ✅ **Pay-per-Use**: Only pay for actual resource consumption
- ✅ **No Server Management**: Focus on code, not infrastructure
- ✅ **High Availability**: Built-in redundancy and failover
- ✅ **Global Performance**: Low latency worldwide

    """)

st.markdown("---")


# Display the architecture diagram
st.markdown("### 📊 Architecture Diagram")

# Path to the SVG file
svg_path = Path(__file__).parent.parent / '.static' / 'architecture.svg'

if svg_path.exists():    
    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()

    st.image(svg_content)
else:
    st.error("⚠️ Architecture diagram not found at `.static/architecture.svg`")
    st.info("Please ensure the architecture.svg file exists in the .static folder.")

st.divider()


# Introduction
st.markdown("""
### About This Design

This application is built using a **modern, serverless architecture** that leverages 
fully managed cloud services. The system is designed with the following key infrastructure:
            """)



# Key components explanation
st.markdown("### 🔑 Infrastructure Components")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### ☁️ Fly.io - Frontend Hosting
    **Streamlit Application in Docker**
    - Multi-page Streamlit app
    - Automatic horizontal scaling
    - Stateful conversation history for chatbots
    - Functional Agentic interactions 
    - Data visualization dashboard
    """)

    st.markdown("""
    #### ☁️ Google Cloud Run - Serverless Backend
    **Dockerized Custom GPT and Image Classification Model APIs**
    - 10M parameter GPT models (Shakespeare and Voyager)
    - Fine-tuned ResNet50 Image Classifier
    - Auto-scaling containers
    - Pay-per-request pricing
    - Zero idle costs
    """)

with col2:
    st.markdown("""
    #### ☁️ Qdrant Cloud - Vector Database
    **Vector Similarity Search**
    - Knowledge base embeddings
    - SOPs and procedures
    - Semantic search
    - RAG (Retrieval Augmented Generation)
    - Auto-scaling
    - High-performance queries
    """)
    
    st.markdown("""
    #### ☁️ Supabase - Database Hosting
    **Managed PostgreSQL**
    - Product catalog, orders, returns & tickets tables for Agent use
    - Automatic backups
    - Connection pooling and read replicas
    - Global availability
    """)
    

st.markdown("---")

# Technology stack
st.markdown("### 🛠️ Technology Stack")

tech_col1, tech_col2, tech_col3 = st.columns(3)

with tech_col1:
    st.markdown("""
    **☁️ Cloud Infrastructure**
    - **Fly.io** (Frontend)
    - **Supabase** (Database)
    - **Qdrant Cloud** (Vectors)
    - **Google Cloud Run & Storage** (Backend & storage)
    - **Docker** (Containers)
    """)

with tech_col2:
    st.markdown("""
    **🤖 AI/ML Frameworks**
    - PyTorch
    - Transformers
    - OpenAI SDK
    - Stability AI SDK
    - NumPy, Pandas
    """)

with tech_col3:
    st.markdown("""
    **💻 Languages & Frameworks**
    - Python 3.x
    - Streamlit
    - PostgreSQL
    - REST APIs
    - Flask/FastAPI                 
    """)

st.divider()

