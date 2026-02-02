import streamlit as st
import requests
import os

st.title("🧠 Custom GPT Model (10M Parameters)")

st.markdown("""
This is a GPT model with 10 million parameters that I trained from scratch.
The model generates text character-by-character based on your parameters.

---
""")

# Configuration
API_URL = os.getenv("BRYCEGPT_API_URL", "http://localhost:8080")

# Sidebar for API configuration
with st.sidebar:
    st.subheader("⚙️ Configuration")
    api_url = st.text_input(
        "API URL",
        value=API_URL,
        help="Your Google Cloud Run API endpoint"
    )
    
    # Test connection
    if st.button("Test Connection"):
        try:
            print(f"Testing connection to {api_url}/health")
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API is reachable!")
            else:
                st.error(f"❌ API returned status {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")

# Main interface
st.markdown("### 🎛️ Generation Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    seed = st.number_input(
        "Seed",
        min_value=0,
        max_value=999999,
        value=42,
        help="Random seed for reproducibility"
    )

with col2:
    temperature = st.slider(
        "Temperature",
        min_value=0.01,
        max_value=2.0,
        value=0.8,
        step=0.01,
        help="Higher = more random, Lower = more deterministic"
    )

with col3:
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=1,
        max_value=500,
        value=100,
        step=10,
        help="Maximum number of tokens to generate"
    )

# Context parameter
st.markdown("### 📝 Context (Optional)")
context_input = st.text_area(
    "Context",
    value="",
    height=100,
    help="Optional context for text generation (leave empty for none)",
    placeholder="Enter context here..."
)

# Generate button
if st.button("🚀 Generate Text", type="primary", use_container_width=True):
    if not api_url:
        st.error("Please provide an API URL in the sidebar")
    else:
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
                
                response = requests.post(
                    f"{api_url}/generate",
                    json=payload,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if response contains the expected "text" field
                    if "text" in result:
                        st.success("✅ Generation complete!")
                        
                        # Display generated text
                        st.markdown("### 📝 Generated Text")
                        st.text_area(
                            "Output",
                            value=result["text"],
                            height=300,
                            disabled=True,
                            label_visibility="collapsed"
                        )
                        
                        # Display generation details
                        with st.expander("ℹ️ Generation Details"):
                            details = {}
                            if "generation_time" in result:
                                details["Generation Time (seconds)"] = result["generation_time"]
                            if "tokens" in result:
                                details["Number of Tokens"] = len(result["tokens"])
                                details["Tokens"] = result["tokens"]
                            details["Request Parameters"] = payload
                            st.json(details)
                    else:
                        st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                        
                        # Display full response for debugging
                        with st.expander("🔍 Full Response Details"):
                            st.json(result)
                        
                        # Display request parameters that were sent
                        with st.expander("📤 Request Parameters Sent"):
                            st.json(payload)
                elif response.status_code == 422:
                    # Validation error
                    try:
                        error_detail = response.json()
                        st.error(f"⚠️ Validation Error: {error_detail.get('detail', 'Invalid parameters')}")
                        if 'errors' in error_detail:
                            st.json(error_detail['errors'])
                    except:
                        st.error("⚠️ Validation Error: Invalid parameters provided")
                else:
                    error_msg = response.json().get('error', 'Unknown error') if response.content else 'No response'
                    st.error(f"API Error ({response.status_code}): {error_msg}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The model might be taking too long to generate.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Could not connect to API. Make sure the Cloud Run service is deployed and the URL is correct.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Vocabulary section
st.markdown("---")
st.markdown("### 📖 Vocabulary")

if st.button("🔤 Load Vocabulary", use_container_width=True):
    if not api_url:
        st.error("Please provide an API URL in the sidebar")
    else:
        with st.spinner("Loading vocabulary..."):
            try:
                response = requests.get(f"{api_url}/vocab", timeout=10)
                
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
st.markdown("### 📚 How to Use")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Model Parameters:**
    - **Seed**: Controls randomness for reproducible results
    - **Temperature**: Controls creativity vs. consistency (0.01-2.0)
    - **Max Tokens**: Maximum number of tokens to generate (1-500)
    - **Context**: Optional starting context for generation
    """)

with col2:
    st.markdown("""
    **Tips:**
    - Lower temperature (0.3-0.7) for more coherent text
    - Higher temperature (1.0-2.0) for more creative/random text
    - Same seed + parameters = same output
    - Provide context to guide the generation
    """)

st.markdown("---")
st.info("""
**🚀 Deployment Instructions:**

1. Deploy the backend to Google Cloud Run (see `cloud_run/README.md`)
2. Get your Cloud Run service URL
3. Set the `GPT_API_URL` environment variable in your Fly.io deployment
4. Or enter the URL in the sidebar configuration
""")
