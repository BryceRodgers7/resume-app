import streamlit as st

def show():
    st.title("🧠 Custom GPT Model (11M Parameters)")
    
    st.markdown("""
    This is a GPT model with 11 million parameters that I trained from scratch.
    
    ---
    """)
    
    st.info("""
    **🔧 Ready to integrate your existing code!**
    
    Replace this placeholder with your GPT model demo code.
    
    Tips for integration:
    - Ensure model loading is cached with `@st.cache_resource`
    - Handle model file paths appropriately
    - Consider adding loading indicators for better UX
    - Update any deprecated PyTorch or Streamlit functions
    """)
    
    st.markdown("### Example Structure:")
    st.code("""
import torch

@st.cache_resource
def load_model():
    # Load your model here
    model = YourGPTModel()
    model.load_state_dict(torch.load('path/to/model.pt'))
    return model

model = load_model()

# Your demo UI here
user_input = st.text_area("Enter text to generate:")
if st.button("Generate"):
    with st.spinner("Generating..."):
        output = model.generate(user_input)
        st.write(output)
    """, language="python")
    
    st.markdown("---")
    st.warning("**Note:** Once you paste your code here, remove the placeholder content above.")
