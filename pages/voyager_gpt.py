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

st.title("🧠 Custom-Trained Language Models")

st.markdown("""
### 10-Million Parameter GPT Models Trained from Scratch

These are **custom-built GPT (Generative Pre-trained Transformer)** models with 10 million parameters that I wrote myself using PyTorch.\n
Choose between **Shakespeare** (trained on Shakespeare's works) or **Voyager** (trained on Star Trek Voyager scripts).
This demonstrates understanding of transformer architecture, model training pipelines, and cloud deployment of multiple ML models.
""")

with st.expander("🎯 What This Demonstrates", expanded=False):
    st.markdown("""
    - **Deep Learning Fundamentals**: Built and trained a transformer-based language model from the ground up
    - **Model Training**: Custom training pipeline with PyTorch, including:
      - Tokenization and vocabulary building
      - Attention mechanisms and positional encoding
      - Loss calculation and optimization
      - Hyperparameter tuning
    - **MLOps & Deployment**: Models deployed as a REST API on Google Cloud Run with containerization
    - **Character-Level Generation**: Models generate text character-by-character
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
    **Example Contexts (Voyager Model):**
    - PARIS: Warp engines are offline!
    - JANEYWAY: Captain's log, stardate 51390.4
    
    **Example Contexts (Shakespeare Model):**
    - To be or not to be
    - Once upon a midnight dreary
    
    **Tips:**
    - **Lower temperature (0.3-0.7)**: More coherent, focused text
    - **Higher temperature (1.0-2.0)**: More creative, random text
    - **Same seed + parameters**: Reproducible output for testing
    - **Continuous generation**: Generated text is automatically appended to build longer narratives
    """)

st.info("🏗️ **Infrastructure**: This model runs on Google Cloud Run with automatic scaling. When idle, the service scales to zero (no cost). Use the 'Check API Status' button in the sidebar to verify the connection. Generation may take 5-10 seconds depending on context size and max tokens.")

st.divider()

# Configuration
API_URL = os.getenv("BRYCEGPT_API_URL", "http://localhost:8080")

# Initialize API health check state
if "api_health_checked" not in st.session_state:
    st.session_state.api_health_checked = False
    st.session_state.api_healthy = None  # None = not checked yet
    st.session_state.api_status_message = "⏳ API status not checked yet"

# Function to check API health (called only when needed)
def check_api_health():
    """Check API health - called on-demand rather than blocking page load."""
    try:
        # Use shorter timeout to avoid blocking
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            st.session_state.api_healthy = True
            st.session_state.api_status_message = "✅ API is connected and ready!"
        else:
            st.session_state.api_healthy = False
            st.session_state.api_status_message = f"❌ API returned status {response.status_code}"
    except requests.exceptions.Timeout:
        st.session_state.api_healthy = False
        st.session_state.api_status_message = "⏱️ API health check timed out (may need cold start time)"
    except Exception as e:
        st.session_state.api_healthy = False
        st.session_state.api_status_message = f"❌ Could not connect to API: {str(e)}"
    st.session_state.api_health_checked = True

# Sidebar for generation parameters
with st.sidebar:
    # API Status
    st.subheader("🔌 API Status")
    
    # Check API health button
    if st.button("🔄 Check API Status", use_container_width=True):
        with st.spinner("Checking API..."):
            check_api_health()
        st.rerun()
    
    if st.session_state.api_healthy is None:
        st.info(st.session_state.api_status_message)
        st.caption("Click 'Check API Status' to verify connection")
    elif st.session_state.api_healthy:
        st.success(st.session_state.api_status_message)
    else:
        st.error(st.session_state.api_status_message)
        st.caption(f"Endpoint: {API_URL}")
    
    # Generation parameters
    st.subheader("🎛️ Generation Parameters")
    
    model = st.selectbox(
        "Model",
        options=["shakespeare", "voyager"],
        index=0,
        help="Choose which model to use for text generation"
    )
    
    seed = st.number_input(
        "Seed",
        min_value=0,
        max_value=999999,
        value=42,
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
st.markdown("Provide starting text to guide the model's generation. Generated text will be automatically appended to continue building your story.")

# Initialize context in session state if not exists
if "context_text" not in st.session_state:
    st.session_state.context_text = ""

# Initialize generating state
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# Text area is disabled during generation
# Use value parameter instead of key to allow programmatic updates
context_input = st.text_area(
    "Starting text",
    value=st.session_state.context_text,
    height=300,
    help="Optional context for text generation (leave empty for none)",
    placeholder="Enter your starting text here...",
    disabled=st.session_state.is_generating
)

# Update session state with current value (unless generating)
if not st.session_state.is_generating:
    st.session_state.context_text = context_input

st.caption("💡 Try: 'To be or not to be' (Shakespeare) | 'Shields down, warp engines are offline' (Voyager)")

# Initialize session state for results
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "result_data" not in st.session_state:
    st.session_state.result_data = None

# Main interface - Generate button
if st.button("🚀 Generate Text", type="primary", use_container_width=True, disabled=st.session_state.is_generating):
    # Capture the current context before setting generating state
    current_context = st.session_state.context_text
    
    # Set generating state and rerun to update UI immediately
    st.session_state.is_generating = True
    st.rerun()

# If we're generating, run the generation process
if st.session_state.is_generating:
    # Get the context that was saved when button was clicked
    current_context = st.session_state.context_text
    
    # Clear previous results
    st.session_state.show_results = False
    st.session_state.result_data = None
    
    # Check API health on first generate if not checked yet
    if st.session_state.api_healthy is None:
        with st.spinner("Checking API connection..."):
            check_api_health()
    
    if not st.session_state.api_healthy:
        st.session_state.is_generating = False
        st.error("⚠️ API is not available. Please check the connection using the 'Check API Status' button in the sidebar.")
        st.stop()
    
    with st.spinner("Generating text..."):
        try:
            # Make API request
            context_value = None
            if current_context.strip():
                # Convert context to array of characters or tokens
                context_value = list(current_context.strip())
            
            payload = {
                "seed": int(seed),
                "temperature": float(temperature),
                "max_tokens": int(max_tokens),
                "context": context_value,
                "model": model
            }
            
            # Log the request for debugging
            logger.info(f"Making API request with model={model}, seed={seed}, temperature={temperature}, max_tokens={max_tokens}, context_length={len(context_value) if context_value else 0}")
            
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
                    logger.info(f"Current context length: {len(current_context)}, API response length: {len(result['text'])}, max_tokens: {max_tokens}")
                    
                    # Extract only the last max_tokens characters (the newly generated portion)
                    # The API returns context + generated text, so the last portion is new
                    generated_only = result["text"][-max_tokens:] if len(result["text"]) >= max_tokens else result["text"]
                    logger.info(f"Extracted last {len(generated_only)} characters as newly generated text")
                    
                    # Update context with the new generated text
                    st.session_state.context_text = current_context + generated_only
                    
                    # Store results in session state for details display
                    st.session_state.show_results = True
                    st.session_state.result_data = {
                        "text": generated_only,  # Store only the newly generated portion
                        "generation_time": result.get("generation_time"),
                        "tokens": result.get("tokens"),
                        "payload": payload,
                        "success": True
                    }
                    
                    # Clear generating state
                    st.session_state.is_generating = False
                    st.rerun()
                else:
                    st.session_state.show_results = True
                    st.session_state.result_data = {
                        "success": False,
                        "error": result.get('error', 'Unknown error'),
                        "full_response": result,
                        "payload": payload
                    }
                    st.session_state.is_generating = False
                    st.rerun()
            elif response.status_code == 422:
                # Validation error
                st.session_state.is_generating = False
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
                st.session_state.is_generating = False
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
            st.session_state.is_generating = False
            logger.error("Request timed out")
            st.error("⏱️ Request timed out. The model might be taking too long to generate.")
        except requests.exceptions.ConnectionError as e:
            st.session_state.is_generating = False
            logger.error(f"Connection error: {str(e)}")
            st.error("🔌 Could not connect to API. Make sure the Cloud Run service is deployed and the URL is correct.")
        except Exception as e:
            st.session_state.is_generating = False
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            st.error(f"❌ Error: {str(e)}")

# Display results if available
if st.session_state.show_results and st.session_state.result_data:
    result_data = st.session_state.result_data
    
    if result_data.get("success"):
        st.success("✅ Generation complete! Text has been appended to the context above.")
        
        # Display generation details
        with st.expander("ℹ️ Generation Details"):
            details = {}
            if result_data.get("generation_time"):
                details["Generation Time (seconds)"] = result_data["generation_time"]
            if result_data.get("tokens"):
                details["Number of Tokens"] = len(result_data["tokens"])
                details["Tokens"] = result_data["tokens"]
            if result_data.get("text"):
                details["Generated Text Length"] = len(result_data["text"])
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
    # Check API health first if not checked yet
    if st.session_state.api_healthy is None:
        with st.spinner("Checking API connection..."):
            check_api_health()
    
    if not st.session_state.api_healthy:
        st.error("⚠️ API is not available. Please check the connection using the 'Check API Status' button in the sidebar.")
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
