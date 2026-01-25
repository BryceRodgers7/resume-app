import streamlit as st
import requests
import os

st.title("🧠 Custom GPT Model (11M Parameters)")

st.markdown("""
This is a GPT model with 11 million parameters that I trained from scratch.
The model generates text character-by-character based on your parameters.

---
""")

# Configuration
API_URL = os.getenv("GPT_API_URL", "http://localhost:8080")

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
        min_value=0.1,
        max_value=2.0,
        value=0.8,
        step=0.1,
        help="Higher = more random, Lower = more deterministic"
    )

with col3:
    num_chars = st.number_input(
        "Characters to Generate",
        min_value=1,
        max_value=5000,
        value=500,
        step=50,
        help="Number of characters to generate"
    )

# Generate button
if st.button("🚀 Generate Text", type="primary", use_container_width=True):
    if not api_url:
        st.error("Please provide an API URL in the sidebar")
    else:
        with st.spinner("Generating text..."):
            try:
                # Make API request
                payload = {
                    "seed": int(seed),
                    "temperature": float(temperature),
                    "num_chars": int(num_chars)
                }
                
                response = requests.post(
                    f"{api_url}/generate",
                    json=payload,
                    timeout=300
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success"):
                        st.success("✅ Generation complete!")
                        
                        # Display generated text
                        st.markdown("### 📝 Generated Text")
                        st.text_area(
                            "Output",
                            value=result["generated_text"],
                            height=300,
                            disabled=True,
                            label_visibility="collapsed"
                        )
                        
                        # Display parameters used
                        with st.expander("ℹ️ Generation Details"):
                            params = result.get("parameters", {})
                            st.json(params)
                    else:
                        st.error(f"Generation failed: {result.get('error', 'Unknown error')}")
                else:
                    error_msg = response.json().get('error', 'Unknown error') if response.content else 'No response'
                    st.error(f"API Error ({response.status_code}): {error_msg}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The model might be taking too long to generate.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Could not connect to API. Make sure the Cloud Run service is deployed and the URL is correct.")
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
    - **Temperature**: Controls creativity vs. consistency
    - **Characters**: How many characters to generate
    """)

with col2:
    st.markdown("""
    **Tips:**
    - Lower temperature (0.3-0.7) for more coherent text
    - Higher temperature (1.0-2.0) for more creative/random text
    - Same seed + parameters = same output
    """)

st.markdown("---")
st.info("""
**🚀 Deployment Instructions:**

1. Deploy the backend to Google Cloud Run (see `cloud_run/README.md`)
2. Get your Cloud Run service URL
3. Set the `GPT_API_URL` environment variable in your Fly.io deployment
4. Or enter the URL in the sidebar configuration
""")
