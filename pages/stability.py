import streamlit as st
import io
import json
import os
from PIL import Image
import requests
import time
import getpass
from random import randrange

# Page configuration
st.set_page_config(
    page_title="Text-to-Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# current_content = io.BytesIO()

st.title("🎨 Text-to-Image Generation")

st.markdown("""
### AI-Powered Image Generation with Stability AI

This demo showcases integration with **Stability AI's SD3 (Stable Diffusion 3)** model for text-to-image generation. 
Enter a text prompt and watch as the AI creates a unique image based on your description.
""")

with st.expander("🎯 What This Demonstrates", expanded=False):
    st.markdown("""
    - **External API Integration**: Direct integration with Stability AI's REST API
    - **File Handling**: Processing and displaying binary image data from API responses
    - **Caching Strategy**: Smart result caching to improve performance and reduce costs
    - **Error Handling**: NSFW content filtering and graceful error management
    - **Image Downloads**: User-friendly download functionality for generated images
    - **Cost Management**: Awareness of API costs and resource optimization
    """)

with st.expander("🔧 How It Works", expanded=False):
    st.markdown("""
    **Technical Process:**
    1. User enters a text description
    2. Request sent to Stability AI SD3 API
    3. Model generates 1024x1024 image
    4. Binary image data returned and cached
    5. Image displayed with download option
    
    **Features:**
    - **Model**: Stable Diffusion 3 Medium
    - **Resolution**: 1:1 aspect ratio
    - **Format**: JPEG output
    - **NSFW Filter**: Automatic content moderation
    - **Caching**: Results cached to avoid duplicate API calls
    """)

with st.expander("💡 Examples to Try", expanded=False):
    st.markdown("""
    **Nature & Landscapes:**
    - "A serene mountain landscape with a crystal clear lake at dawn"
    - "An ancient forest with sunlight filtering through massive trees"
    
    **Sci-Fi & Fantasy:**
    - "A futuristic city at sunset with flying vehicles"
    - "A medieval castle on a cliff overlooking the ocean"
    
    **Art & Abstract:**
    - "An abstract painting combining blues and golds with geometric shapes"
    - "A surreal desert scene with impossible architecture"
    
    **Characters & Scenes:**
    - "A futuristic robot reading a book in a cozy library"
    - "A peaceful garden with cherry blossoms and a stone path"
    """)

st.warning("⚠️ **Important**: Each image generation costs $0.25 through the Stability AI API. This demo is intended to show API integration capabilities.")

st.divider()

parrot_path = './.static/parrot.jpg'
parrot_caption = 'A beautiful parrot before a lush background of jungle canopy.'

# get API key from environment variables
if STABILITY_KEY := os.getenv('STABILITY_KEY'):
    st.sidebar.success('Stability AI API key is good.', icon='✅')
else:
    st.sidebar.warning('credentials are not working.', icon='⚠️')

# if 'STABILITY_KEY' in st.secrets:
#     STABILITY_KEY = st.secrets['STABILITY_KEY']
#     st.sidebar.success('API key is good.', icon='✅')
# else:
#     st.sidebar.warning('credentials are not working.', icon='⚠️')

host = f"https://api.stability.ai/v2beta/stable-image/generate/sd3"
st.session_state.show_pic = False

def send_generation_request(host, params,):
    headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {STABILITY_KEY}"
    }

    # Encode parameters
    files = {}
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image is not None and image != '':
        files["image"] = open(image, 'rb')
    if mask is not None and mask != '':
        files["mask"] = open(mask, 'rb')
    if len(files)==0:
        files["none"] = ''

    # Send request
    print(f"Sending REST request to {host}...")
    response = requests.post(
        host,
        headers=headers,
        files=files,
        data=params
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    return response

def get_bytes(content):
    return io.BytesIO(content)

# def get_image_bytes():
#     return current_content
    
if "show_stability" not in st.session_state:
        st.session_state.show_stability = False

placeholder = st.empty()

@st.cache_data
def hit_stability(prompt):
    params = {
        "prompt" : prompt,
        "aspect_ratio" : "1:1",
        "seed" : 42,
        "output_format" : 'jpeg',
        "model" : "sd3-medium"
    }

    response = send_generation_request(host,params)

    # Decode response
    content = response.content
    finish_reason = response.headers.get("finish-reason")
    # seed = response.headers.get("seed")

    # Check for NSFW classification
    if finish_reason == 'CONTENT_FILTERED':
        raise Warning("Generation failed NSFW classifier")

    return io.BytesIO(content)

# move logic to here later
def fake_hit_stab():
    time.sleep(1)


#img_prompt = st.text_area("What would you like to see? RANDOM IMAGES ENABLED", "A beautiful parrot before a lush background of jungle canopy.")
img_prompt = st.text_area("What would you like to see?", parrot_caption)
st.divider()
click = st.button("See It!", help="submit your prompt and get an image", use_container_width=False)

def fragment_function(img_BufferedReader):
    dl_click = st.download_button(
      label="Download Image",
      data=img_BufferedReader,
      file_name="generated_image.png",
      mime="image/jpeg",
      )

if click:
    st.session_state.show_stability = True
    
if st.session_state.show_stability:
    #fake_hit_stab(img_prompt, placeholder)
    img_bytes = hit_stability(img_prompt)
    placeholder = st.image(img_bytes, caption=img_prompt)
    img_BufferedReader = io.BufferedReader(img_bytes)
    fragment_function(img_BufferedReader)
else:
    # st.write('sample image...')
    fake_hit_stab()
    placeholder = st.image(parrot_path, caption=parrot_caption)
    img_bytes = '' # get img bytes for pregenerated file later
    

    
# st.button("clear it!", help="clear the image", on_click=clear_image(), use_container_width=False)