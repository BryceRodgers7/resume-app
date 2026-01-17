import streamlit as st

st.title("🎨 Text-to-Image Generator")

st.markdown("""
Generate images from text descriptions using Stability AI's API.

---
""")

st.info("""
**🔧 Ready to integrate your existing code!**

Replace this placeholder with your text-to-image generator code.

Tips for integration:
- Store API keys in `.streamlit/secrets.toml` or environment variables
- Use `@st.cache_data` for caching generated images
- Add proper error handling for API calls
- Consider adding image parameter controls (size, style, etc.)
""")

st.markdown("### Example Structure:")
st.code("""
import requests
from PIL import Image
import io

# Get API key from secrets
api_key = st.secrets.get("STABILITY_API_KEY", "")

# UI
prompt = st.text_area("Enter your image description:")
if st.button("Generate Image"):
    if not api_key:
        st.error("Please add STABILITY_API_KEY to secrets")
    else:
        with st.spinner("Generating image..."):
            # Your API call here
            response = generate_image(prompt, api_key)
            image = Image.open(io.BytesIO(response.content))
            st.image(image, caption=prompt)
""", language="python")

st.markdown("---")
st.warning("**Note:** Once you paste your code here, remove the placeholder content above.")
