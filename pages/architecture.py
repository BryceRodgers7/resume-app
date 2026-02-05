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

#### ☁️ Deployment Infrastructure
- **Fly.io**: Frontend hosting (Streamlit in Docker container)
- **Supabase**: Managed PostgreSQL database
- **Qdrant Cloud**: Vector database for knowledge base
- **Google Cloud Run**: Serverless backend for Custom GPT API
- **OpenAI & Stability AI**: External API services

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
        <div style="width: 100%; height: 950px; overflow: auto; border: 1px solid #ddd; border-radius: 5px; background: white;">
            {svg_content}
        </div>
        """,
        height=1300,
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
    - Customer Support chatbot (agentic)
    - Pirate Chatbot (simple conversational AI)
    - Custom GPT Model interface
    - Image Classifier (PyTorch inference)
    - Text-to-Image generator
    - Data visualization dashboard
    - Automatic horizontal scaling
    """)
    
    st.markdown("""
    #### ☁️ Supabase - Database Hosting
    **Managed PostgreSQL**
    - Products catalog
    - Order management
    - Returns processing
    - Support ticket tracking
    - Automatic backups
    - Connection pooling
    - Real-time capabilities
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
    #### ☁️ Google Cloud Run - Serverless Backend
    **Custom GPT Model API**
    - 10M parameter GPT model
    - Character-level generation
    - Auto-scaling containers
    - Pay-per-request pricing
    - Zero idle costs
    """)

st.markdown("---")

st.markdown("### 🤖 Application Features")

feat_col1, feat_col2 = st.columns(2)

with feat_col1:
    st.markdown("""
    #### Agentic Support System
    - **GPT-4 Powered Agent**: Intelligent orchestrator
    - **Tool Architecture**: Extensible function calling
    - **Available Tools**: Order mgmt, product search, KB retrieval
    - **RAG System**: Context-aware responses
    - **Conversation History**: Multi-turn conversations
    """)

with feat_col2:
    st.markdown("""
    #### ML & AI Capabilities
    - **Custom PyTorch Models**: Image classification
    - **Text Generation**: GPT-3.5, GPT-4, Custom GPT
    - **Image Generation**: Stability AI SD3
    - **Embeddings**: OpenAI for vector search
    - **Transfer Learning**: ResNet18 fine-tuning
    """)

st.divider()

# Data flow examples
st.markdown("### 🔄 Example Data Flows")

with st.expander("📞 Customer Support Query Flow"):
    st.markdown("""
    1. **User** sends message via Streamlit UI
    2. **Agent** (`chatbot/agent.py`) receives message
    3. **Agent** calls OpenAI with system prompt and available tools
    4. **OpenAI** decides which tools to call (e.g., `search_products`)
    5. **Tool Implementation** executes database or vector store query
    6. **Results** returned to OpenAI for natural language synthesis
    7. **Agent** returns response to UI with tool usage tracking
    """)

with st.expander("🖼️ Image Classification Flow"):
    st.markdown("""
    1. **User** uploads image via Streamlit UI
    2. **Image** preprocessed (resize to 224x224, normalize)
    3. **PyTorch Model** performs inference (ResNet18)
    4. **Confidence Thresholding** applied (default 60%)
    5. **Predictions** displayed with probability breakdown
    """)

with st.expander("🤖 Custom GPT Generation Flow"):
    st.markdown("""
    1. **User** configures parameters (seed, temperature, max_tokens)
    2. **Request** sent to Google Cloud Run API
    3. **Model** generates text character-by-character
    4. **Response** streamed back to UI
    5. **Display** generation time and token information
    """)

with st.expander("🎨 Text-to-Image Generation Flow"):
    st.markdown("""
    1. **User** enters text prompt
    2. **Request** sent to Stability AI API (SD3 model)
    3. **Image** generated based on prompt
    4. **Result** displayed with download option
    5. **Cached** for performance (using Streamlit caching)
    """)

st.divider()

# Why Serverless section
st.markdown("### ☁️ Why This Architecture is Serverless")

serverless_col1, serverless_col2 = st.columns(2)

with serverless_col1:
    st.markdown("""
    #### No Server Management
    - All infrastructure fully managed
    - No SSH access or server config
    - Automatic OS updates & security patches
    - Focus on code, not servers
    
    #### Automatic Scaling
    - **Fly.io**: Scales containers based on traffic
    - **Supabase**: Connection pooling & read replicas
    - **Qdrant Cloud**: Managed scaling
    - **Cloud Run**: Scales to zero when idle
    """)

with serverless_col2:
    st.markdown("""
    #### Pay-per-Use Pricing
    - Only pay for actual consumption
    - No cost for idle resources
    - Predictable pricing
    - Cost-efficient for variable traffic
    
    #### High Availability
    - Built-in redundancy
    - Automatic failover
    - Geographic distribution
    - 99.9%+ uptime SLAs
    """)

st.divider()

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
st.caption("Built with Streamlit • Powered by OpenAI, PyTorch, and Stability AI")
