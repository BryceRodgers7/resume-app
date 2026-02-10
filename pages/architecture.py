import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Resume App Architecture",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏗️ Resume App Architecture")

st.markdown("""
This diagram shows the complete **serverless/cloud-native** architecture of the AI Portfolio 
application, including deployment infrastructure, application components, and external services.

---
""")

# Architecture type badge
st.info("🚀 **Architecture Type**: Serverless / Cloud-Native - No server management required!")

# Introduction
st.markdown("""
### About This Architecture

This portfolio application is built using a **modern, serverless architecture** that leverages 
fully managed cloud services. The system is designed with the following key infrastructure:
            """)

deployment_col1, deployment_col2 = st.columns(2)

with deployment_col1:
    st.markdown("""
#### ☁️ Deployment Infrastructure
- **Fly.io**: Frontend hosting (Streamlit in Docker container)
- **Supabase**: Managed PostgreSQL database
- **Qdrant Cloud**: Vector database for knowledge base
- **Google Cloud Run**: Serverless backend for Custom GPT API
- **OpenAI & Stability AI**: External API services
    
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


st.divider()

# Display the architecture diagram
st.markdown("### 📊 Architecture Diagram")

# Path to the SVG file
svg_path = Path(__file__).parent.parent / '.static' / 'architecture.svg'

if svg_path.exists():
    # Read the SVG file
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Display SVG using HTML iframe for better rendering
    components.html(
        f"""
        <div style="width: 100%; height: 1400px; overflow: auto; border: 1px solid #ddd; border-radius: 5px; background: white;">
            {svg_content}
        </div>
        """,
        height=1450,
        scrolling=True
    )
else:
    st.error("⚠️ Architecture diagram not found at `.static/architecture.svg`")
    st.info("Please ensure the architecture.svg file exists in the .static folder.")

st.divider()

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
    - Functional interactions 
    - Data visualization dashboard
    """)

    st.markdown("""
    #### ☁️ Google Cloud Run - Serverless Backend
    **Custom GPT Model API**
    - 10M parameter GPT model
    - Character-level generation
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
    - Products catalog, orders, returns, tickets
    - Automatic backups
    - Connection pooling
    - Real-time capabilities
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
    - **Google Cloud Run** (Backend)
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
    - WebSockets
    """)

st.markdown("---")
