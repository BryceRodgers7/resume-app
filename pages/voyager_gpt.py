import streamlit as st
import requests
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Page configuration
st.set_page_config(
    page_title="Custom GPT Model",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧠 VoyagerGPT: Custom-Trained Language Model")

st.markdown("""
### 10-Million Parameter GPT Model Trained from Scratch

This is a **custom-built GPT (Generative Pre-trained Transformer)** with 10 million parameters that I built and trained from scratch. 
It demonstrates understanding of transformer architecture, model training pipelines, and cloud deployment of ML inference services.
""")

with st.expander("🎯 What This Demonstrates", expanded=False):
    st.markdown("""
    - **Deep Learning Fundamentals**: Built and trained a transformer-based language model from the ground up
    - **Model Training**: Custom training pipeline with PyTorch, including:
      - Tokenization and vocabulary building
      - Attention mechanisms and positional encoding
      - Loss calculation and optimization
      - Hyperparameter tuning
    - **MLOps & Deployment**: Model deployed as a REST API on Google Cloud Run with containerization
    - **Character-Level Generation**: Model generates text character-by-character for fine-grained control
    - **API Design**: RESTful endpoints for text generation and vocabulary inspection
    - **Cloud Infrastructure**: Serverless deployment with automatic scaling and cost optimization
    """)

with st.expander("🔧 Technical Architecture", expanded=False):
    st.markdown("""
    **Model Specifications:**
    - **Parameters**: 10 million trainable parameters
    - **Architecture**: GPT-style decoder-only transformer
    - **Training**: Custom dataset with domain-specific content
    - **Inference**: Hosted on Google Cloud Run (serverless)
    - **API**: FastAPI with Pydantic validation

    **Generation Controls:**
    - **Seed**: Reproducible generation for testing and debugging
    - **Temperature**: Control creativity vs. consistency (0.01-2.0)
    - **Max Tokens**: Configurable output length (1-500 tokens)
    - **Context**: Optional prompt to guide generation
    """)

with st.expander("💡 Try it Out", expanded=False):
    st.markdown("""
    **Example Contexts:**
    - "Voyager encounters an undiscovered wormhole"
    - "PARIS: Warp engines are offline!"
    - "JANEYWAY: Captain's log, stardate 51390.4"
    
    **Tips:**
    - **Lower temperature (0.3-0.7)**: More coherent, focused text
    - **Higher temperature (1.0-2.0)**: More creative, random text
    - **Same seed + parameters**: Reproducible output for testing
    - **Append feature**: Build longer narratives by generating iteratively
    """)

st.info("🏗️ **Infrastructure**: This model runs on Google Cloud Run with automatic scaling. When idle, the service scales to zero (no cost). The API wakes up on first request (~5-10 second cold start). Generation may take 30 seconds or more.")

st.divider()

# Configuration
API_URL = os.getenv("BRYCEGPT_API_URL", "http://localhost:8080")

# Check API health on page load (once per session)
if "api_health_checked" not in st.session_state:
    st.session_state.api_health_checked = False
    st.session_state.api_healthy = False
    st.session_state.api_status_message = ""

if not st.session_state.api_health_checked:
    try:
        # Use longer timeout for cold starts (Cloud Run may need time to wake up)
        response = requests.get(f"{API_URL}/health", timeout=30)
        if response.status_code == 200:
            st.session_state.api_healthy = True
            st.session_state.api_status_message = "✅ API is connected and ready!"
        else:
            st.session_state.api_healthy = False
            st.session_state.api_status_message = f"❌ API returned status {response.status_code}"
    except requests.exceptions.Timeout:
        st.session_state.api_healthy = False
        st.session_state.api_status_message = "⏱️ API health check timed out (cold start may need more time). Try refreshing."
    except Exception as e:
        st.session_state.api_healthy = False
        st.session_state.api_status_message = f"❌ Could not connect to API: {str(e)}"
    st.session_state.api_health_checked = True

# Sidebar for generation parameters
with st.sidebar:
    # API Status
    st.subheader("🔌 API Status")
    if st.session_state.api_healthy:
        st.success(st.session_state.api_status_message)
    else:
        st.error(st.session_state.api_status_message)
        st.caption(f"Endpoint: {API_URL}")
    
    # Generation parameters
    st.subheader("🎛️ Generation Parameters")
    
    seed = st.number_input(
        "Seed",
        min_value=0,
        max_value=999999,
        value=1337,
        help="Random seed for reproducibility"
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.01,
        max_value=2.0,
        value=0.8,
        step=0.01,
        help="Higher = more random, Lower = more deterministic"
    )
    
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=1,
        max_value=500,
        value=100,
        step=10,
        help="Maximum number of tokens to generate"
    )

# Context parameter on main page
st.markdown("### 📝 Context (Optional)")
st.markdown("Provide starting text to guide the model's generation. Generated text can be appended to build a running episode script.")

# Initialize context in session state if not exists
if "context_input" not in st.session_state:
    st.session_state.context_input = ""

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""

# Don't use value parameter when using key - it's controlled by session state
context_input = st.text_area(
    "Starting text",
    height=200,
    help="Optional context for text generation (leave empty for none)",
    placeholder="Once upon a time in a distant galaxy...",
    key="context_input"
)

st.caption("💡 Try: 'Once upon a time' or 'In the year 2372, voyager encounters'")

# Initialize session state for results
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "result_data" not in st.session_state:
    st.session_state.result_data = None

# Main interface - Generate button
if st.button("🚀 Generate Text", type="primary", use_container_width=True):
    if not st.session_state.api_healthy:
        st.error("⚠️ API is not available. Please check the connection status in the sidebar.")
        st.stop()
    
    with st.spinner("Generating text..."):
        try:
            # Make API request
            context_value = None
            if context_input.strip():
                # Convert context to array of characters or tokens
                context_value = list(context_input.strip())
            
            payload = {
                "seed": int(seed),
                "temperature": float(temperature),
                "max_tokens": int(max_tokens),
                "context": context_value
            }
            
            # Log the request for debugging
            logger.info(f"Making API request with seed={seed}, temperature={temperature}, max_tokens={max_tokens}, context_length={len(context_value) if context_value else 0}")
            
            response = requests.post(
                f"{API_URL}/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if response contains the expected "text" field
                if "text" in result:
                    # Log successful generation
                    text_preview = result["text"][:50] + "..." if len(result["text"]) > 50 else result["text"]
                    logger.info(f"Successfully generated text (preview): {text_preview}")
                    
                    # Store results in session state
                    st.session_state.show_results = True
                    st.session_state.result_data = {
                        "text": result["text"],
                        "generation_time": result.get("generation_time"),
                        "tokens": result.get("tokens"),
                        "payload": payload,
                        "success": True
                    }
                    st.rerun()
                else:
                    st.session_state.show_results = True
                    st.session_state.result_data = {
                        "success": False,
                        "error": result.get('error', 'Unknown error'),
                        "full_response": result,
                        "payload": payload
                    }
                    st.rerun()
            elif response.status_code == 422:
                # Validation error
                try:
                    error_detail = response.json()
                    logger.error(f"Validation error (422): {error_detail}")
                    st.error(f"⚠️ Validation Error: {error_detail.get('detail', 'Invalid parameters')}")
                    if 'errors' in error_detail:
                        st.json(error_detail['errors'])
                except:
                    st.error("⚠️ Validation Error: Invalid parameters provided")
            else:
                # Log full error details for debugging
                try:
                    error_response = response.json()
                    logger.error(f"API Error {response.status_code}:")
                    logger.error(f"  Response: {error_response}")
                    logger.error(f"  Payload sent: {payload}")
                    error_msg = error_response.get('error', 'Unknown error')
                except:
                    logger.error(f"API Error {response.status_code}: Could not parse response")
                    logger.error(f"  Response content: {response.content}")
                    logger.error(f"  Payload sent: {payload}")
                    error_msg = 'Unknown error'
                
                st.error(f"API Error ({response.status_code}): {error_msg}")
                
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            st.error("⏱️ Request timed out. The model might be taking too long to generate.")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            st.error("🔌 Could not connect to API. Make sure the Cloud Run service is deployed and the URL is correct.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            st.error(f"❌ Error: {str(e)}")

# Display results if available
if st.session_state.show_results and st.session_state.result_data:
    result_data = st.session_state.result_data
    
    if result_data.get("success"):
        st.success("✅ Generation complete!")
        
        # Display generated text
        st.markdown("### 📝 Generated Text")
        st.text_area(
            "Output",
            value=result_data["text"],
            height=300,
            disabled=True,
            label_visibility="collapsed",
            key="output_display"
        )
        
        # Callback function for append button
        def append_to_context():
            st.session_state.context_input = st.session_state.context_input + result_data["text"]
        
        # Append to context button
        col1, col2 = st.columns([1, 3])
        with col1:
            st.button(
                "➕ Append to Context", 
                use_container_width=True, 
                help="Add this generated text to the context above for continued generation",
                on_click=append_to_context
            )
        
        with col2:
            st.caption("💡 Click to add this text to your context for continued generation")
        
        # Display generation details
        with st.expander("ℹ️ Generation Details"):
            details = {}
            if result_data.get("generation_time"):
                details["Generation Time (seconds)"] = result_data["generation_time"]
            if result_data.get("tokens"):
                details["Number of Tokens"] = len(result_data["tokens"])
                details["Tokens"] = result_data["tokens"]
            details["Request Parameters"] = result_data["payload"]
            st.json(details)
    else:
        st.error(f"❌ Generation failed: {result_data.get('error', 'Unknown error')}")
        
        # Display full response for debugging
        with st.expander("🔍 Full Response Details"):
            st.json(result_data.get("full_response", {}))
        
        # Display request parameters that were sent
        with st.expander("📤 Request Parameters Sent"):
            st.json(result_data.get("payload", {}))

# Vocabulary section
st.markdown("---")
st.markdown("### 📖 Model Vocabulary")

if st.button("🔤 Load Vocabulary", use_container_width=True):
    if not st.session_state.api_healthy:
        st.error("⚠️ API is not available. Please check the connection status in the sidebar.")
    else:
        with st.spinner("Loading vocabulary..."):
            try:
                response = requests.get(f"{API_URL}/vocab", timeout=20)
                
                if response.status_code == 200:
                    vocab_data = response.json()
                    st.success("✅ Vocabulary loaded!")
                    
                    # Display vocabulary information
                    if isinstance(vocab_data, dict):
                        vocab_size = vocab_data.get("vocab_size", len(vocab_data.get("vocab", [])))
                        st.metric("Vocabulary Size", vocab_size)
                        
                        with st.expander("View Vocabulary Details"):
                            st.json(vocab_data)
                    else:
                        st.json(vocab_data)
                else:
                    st.error(f"Failed to load vocabulary: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Could not connect to API.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Information section
st.markdown("---")
st.markdown("### 📚 Technical Details")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Model Architecture:**
    - Transformer decoder blocks
    - Multi-head self-attention
    - Positional encoding
    - Layer normalization
    - Feed-forward networks
    
    **Training Pipeline:**
    - Custom PyTorch implementation
    - Character-level tokenization
    - Gradient clipping and optimization
    - Checkpointing and validation
    """)

with col2:
    st.markdown("""
    **Generation Parameters:**
    - **Seed**: Controls randomness for reproducible results
    - **Temperature**: Higher = more creative, Lower = more deterministic
    - **Max Tokens**: Output length control
    - **Context**: Starting prompt for guided generation
    
    **Tips:**
    - Temperature 0.3-0.7: Coherent, focused text
    - Temperature 1.0-2.0: Creative, random text
    - Same seed + parameters = deterministic output
    """)

st.divider()

st.markdown("""
### 🚀 Deployment Architecture

This model is deployed as a **serverless microservice** on Google Cloud Run:

- **Containerized API**: Docker container with PyTorch model
- **Auto-scaling**: Scales from 0 to N instances based on traffic
- **Cost-Efficient**: Only pay for actual inference time (scale to zero when idle)
- **API Gateway**: RESTful endpoints with request validation
- **Model Serving**: Efficient inference with batch processing support

The frontend (this page) communicates with the backend API via HTTPS, demonstrating **full-stack ML deployment**.
""")
