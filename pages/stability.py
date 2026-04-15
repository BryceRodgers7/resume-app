import streamlit as st
import logging
import os
import sys
import requests
import time
import nav
from app import home_page


def _stability_stderr(msg: str) -> None:
    """Always write to stderr; Fly logs capture this even when page loggers do not propagate."""
    print(f"[stability] {msg}", file=sys.stderr, flush=True)


# Dedicated logger with its own StreamHandler — Streamlit runs page scripts in a context where
# getLogger(__name__) often does not propagate INFO to the root handler, so __main__ logs appear in Fly but not these.
_stability_log = logging.getLogger("stability_fly")
if not _stability_log.handlers:
    _h = logging.StreamHandler(sys.stderr)
    _h.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [stability_fly] %(message)s")
    )
    _stability_log.addHandler(_h)
    _stability_log.setLevel(logging.INFO)
    _stability_log.propagate = False

# Page configuration
st.set_page_config(
    page_title="Text-to-Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

nav.config_navigation(home_page)

if "stability_stderr_boot" not in st.session_state:
    st.session_state.stability_stderr_boot = True
    _stability_stderr("page loaded this browser session (stderr ok)")

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

st.caption(
    "If this tab sat in the background for a long time, **refresh the page** before clicking "
    "See It! — the live connection to the server can go stale while idle (browser / hosting), "
    "which looks like a blank main area while the sidebar still works."
)

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
    _stability_log.info("Sending REST request to %s", host)
    _stability_stderr(f"Sending REST request to {host}")
    response = requests.post(
        host,
        headers=headers,
        files=files,
        data=params,
        timeout=(30, 180),
    )
    if not response.ok:
        body_preview = (response.text or "")[:2000]
        _stability_log.error(
            "Stability API error: status=%s body=%s",
            response.status_code,
            body_preview,
        )
        _stability_stderr(
            f"Stability API error: status={response.status_code} body={body_preview[:500]}"
        )
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    return response

if "show_stability" not in st.session_state:
        st.session_state.show_stability = False

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

    # Cache immutable bytes, not io.BytesIO — st.image() advances the buffer to EOF; the next rerun
    # reuses the cached object and can blank the main pane while the sidebar still renders.
    return content

# move logic to here later
def fake_hit_stab():
    time.sleep(1)


#img_prompt = st.text_area("What would you like to see? RANDOM IMAGES ENABLED", "A beautiful parrot before a lush background of jungle canopy.")
img_prompt = st.text_area("What would you like to see?", parrot_caption)
st.divider()
click = st.button("See It!", help="submit your prompt and get an image", use_container_width=False)

if click:
    _pl = len((img_prompt or "").strip())
    _stability_log.info("'See It!' pressed (prompt_len=%d)", _pl)
    _stability_stderr(f"See It! pressed (prompt_len={_pl})")
    st.session_state.show_stability = True

if st.session_state.show_stability:
    try:
        if click:
            _stability_log.info("starting image generation (same run as button click)")
            _stability_stderr("starting image generation (same run as button click)")
        img_bytes = hit_stability(img_prompt)
        if click:
            _stability_log.info("hit_stability() completed")
            _stability_stderr("hit_stability() completed")
        st.image(img_bytes, caption=img_prompt)
        st.download_button(
            label="Download Image",
            data=img_bytes,
            file_name="generated_image.jpg",
            mime="image/jpeg",
        )
    except Exception:
        _stability_log.exception("Stability page: image generation or display failed")
        _stability_stderr("exception during generation or display (see stability_fly traceback above)")
        st.error(
            "Image generation failed. Details were written to the server log; "
            "check `fly logs` for the full traceback."
        )
else:
    fake_hit_stab()
    st.image(parrot_path, caption=parrot_caption)
    

    
# st.button("clear it!", help="clear the image", on_click=clear_image(), use_container_width=False)